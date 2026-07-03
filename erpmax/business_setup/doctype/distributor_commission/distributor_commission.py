import frappe
from frappe.model.document import Document
from erpmax.utils.naming import sync_transaction_party_fields

class DistributorCommission(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        sync_transaction_party_fields(self)
        if self.distributor and not self.distributor_name:
            self.distributor_name = frappe.db.get_value("Distributor", self.distributor, "distributor_name")
        if self.sales_invoice and not self.customer:
            self.customer = frappe.db.get_value("Sales Invoice", self.sales_invoice, "customer")
        if self.commission_amount <= 0:
            frappe.throw("Commission Amount must be greater than zero")

    def on_submit(self):
        self.make_gl_entries()
        self.status = "Posted"

    def on_cancel(self):
        self.reverse_gl_entries()
        self.status = "Cancelled"

    def make_gl_entries(self):
        """Create GL Entries for commission:
        - Debit: Commission Expense Account
        - Credit: Commission Payable Account
        """
        rows = [
            {"account": self.expense_account, "debit": self.commission_amount, "credit": 0},
            {"account": self.payable_account, "debit": 0, "credit": self.commission_amount},
        ]
        for row in rows:
            gl = frappe.get_doc(
                {
                    "doctype": "GL Entry",
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "account": row["account"],
                    "debit": row["debit"],
                    "credit": row["credit"],
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "party_type": "Distributor",
                    "party": self.distributor,
                    "against_voucher_type": "Sales Invoice",
                    "against_voucher": self.sales_invoice,
                }
            )
            gl.flags.ignore_permissions = True
            gl.insert()

    def reverse_gl_entries(self):
        for gle in frappe.get_all("GL Entry", filters={"voucher_type": self.doctype, "voucher_no": self.name}):
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)


