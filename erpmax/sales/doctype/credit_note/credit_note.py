import frappe
from frappe import _
from frappe.model.document import Document


class CreditNote(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        if not self.outstanding_amount:
            self.outstanding_amount = self.grand_total

    def on_submit(self):
        self.status = "Submitted"
        self.make_gl_entries()
        self.update_original_invoice()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()
        self.revert_original_invoice()

    def make_gl_entries(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        debit_to = customer.default_receivable_account
        income_account = None
        for item in self.items:
            income_account = item.income_account
            break

        entries = []
        if debit_to:
            entries.append({"account": debit_to, "debit": 0, "credit": self.grand_total})
        if income_account:
            entries.append({"account": income_account, "debit": self.total, "credit": 0})
        for tax in self.taxes:
            if tax.account_head:
                entries.append({"account": tax.account_head, "debit": tax.amount, "credit": 0})

        for entry in entries:
            gl = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": entry["account"],
                "debit": entry["debit"],
                "credit": entry["credit"],
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": "Customer",
                "party": self.customer,
            })
            gl.flags.ignore_permissions = True
            gl.insert()

    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

    def update_original_invoice(self):
        if self.against_invoice:
            frappe.db.set_value("Sales Invoice", self.against_invoice, "outstanding_amount",
                frappe.db.get_value("Sales Invoice", self.against_invoice, "outstanding_amount") - self.grand_total)

    def revert_original_invoice(self):
        if self.against_invoice:
            frappe.db.set_value("Sales Invoice", self.against_invoice, "outstanding_amount",
                frappe.db.get_value("Sales Invoice", self.against_invoice, "outstanding_amount") + self.grand_total)
