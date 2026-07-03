import frappe
from frappe.model.document import Document


class InternalAccountTransaction(Document):
    def validate(self):
        if self.amount <= 0:
            frappe.throw("Amount must be greater than zero")
        if self.from_account == self.to_account:
            frappe.throw("From Account and To Account must be different")

    def on_submit(self):
        self.make_gl_entries()

    def on_cancel(self):
        self.reverse_gl_entries()

    def make_gl_entries(self):
        rows = [
            {"account": self.from_account, "debit": 0, "credit": self.amount},
            {"account": self.to_account, "debit": self.amount, "credit": 0},
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
                    "party_type": "Partner Account" if self.partner_account else None,
                    "party": self.partner_account,
                }
            )
            gl.flags.ignore_permissions = True
            gl.insert()

    def reverse_gl_entries(self):
        for gle in frappe.get_all("GL Entry", filters={"voucher_type": self.doctype, "voucher_no": self.name}):
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)
