import frappe
from frappe.model.document import Document

class JournalEntry(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        self.total_debit = sum(row.debit or 0 for row in self.accounts)
        self.total_credit = sum(row.credit or 0 for row in self.accounts)
        if abs(self.total_debit - self.total_credit) > 0.01:
            frappe.throw("Total Debit must equal Total Credit")
        self.validate_account_company()

    def validate_account_company(self):
        for row in self.accounts:
            if row.account:
                acc = frappe.get_cached_doc("Account", row.account)
                if acc.company != self.company:
                    frappe.throw(
                        "Account {0} belongs to {1}, but Journal Entry is for {2}".format(
                            row.account, acc.company, self.company
                        )
                    )

    def on_submit(self):
        self.make_gl_entries()

    def on_cancel(self):
        self.make_reverse_gl_entries()

    def make_gl_entries(self):
        for row in self.accounts:
            if row.debit or row.credit:
                gl = frappe.get_doc({
                    "doctype": "GL Entry",
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "account": row.account,
                    "debit": row.debit or 0,
                    "credit": row.credit or 0,
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "party_type": row.party_type,
                    "party": row.party,
                    "against_voucher_type": None,
                    "against_voucher": None,
                })
                gl.flags.ignore_permissions = True
                gl.insert()

    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

# Module-level hooks wrappers for doc_events

def validate(doc, method):
    pass

def on_submit(doc, method):
    pass

def on_cancel(doc, method):
    pass
