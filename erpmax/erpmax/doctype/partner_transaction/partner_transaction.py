import frappe
from frappe.model.document import Document

from erpmax.utils.naming import sync_transaction_party_fields

class PartnerTransaction(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        sync_transaction_party_fields(self)
        if self.partner_account and not self.partner_name:
            self.partner_name = self.partner_account
        if self.amount <= 0:
            frappe.throw("Amount must be greater than zero")
        if self.debit_account == self.credit_account:
            frappe.throw("Debit and Credit accounts must be different")

    def on_submit(self):
        self.make_gl_entries()

    def on_cancel(self):
        self.reverse_gl_entries()

    def make_gl_entries(self):
        rows = [
            {"account": self.debit_account, "debit": self.amount, "credit": 0},
            {"account": self.credit_account, "debit": 0, "credit": self.amount},
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
                    "party_type": "Partner Account",
                    "party": self.partner_account,
                }
            )
            gl.flags.ignore_permissions = True
            gl.insert()

    def reverse_gl_entries(self):
        for gle in frappe.get_all("GL Entry", filters={"voucher_type": self.doctype, "voucher_no": self.name}):
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

