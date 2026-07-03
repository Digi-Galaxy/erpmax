import frappe
from frappe.model.document import Document
from frappe import _

from erpmax.utils.naming import sync_transaction_party_fields


class PaymentEntry(Document):
    def autoname(self):
        # Set payment direction BEFORE naming so it appears in the name
        self._auto_set_payment_direction()
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def _auto_set_payment_direction(self):
        """Auto-set payment type based on party type before naming."""
        if not self.party_type:
            return
        if self.party_type == "Customer":
            self.payment_type = "Receive"
        elif self.party_type == "Supplier":
            self.payment_type = "Pay"

    def validate(self):
        self._auto_set_payment_direction()
        self._auto_set_accounts()
        sync_transaction_party_fields(self)
        self.total_allocated_amount = sum(
            (row.allocated_amount or 0) for row in (self.references or [])
        )
        self.unallocated_amount = self.paid_amount - self.total_allocated_amount
        self.difference_amount = self.paid_amount - self.received_amount

    def _auto_set_accounts(self):
        """Auto-set paid_from/paid_to accounts based on payment direction."""
        company = self.company
        if not company:
            return
        abbr = frappe.db.get_value("Company", company, "abbreviation") or "GLPK"
        cash_account = f"Cash - {abbr}"
        bank_account = f"Bank - {abbr}"

        if self.payment_type == "Receive":
            if not self.paid_from:
                self.paid_from = cash_account
            if not self.paid_to:
                self.paid_to = bank_account
        elif self.payment_type == "Pay":
            if not self.paid_from:
                self.paid_from = bank_account
            if not self.paid_to:
                self.paid_to = cash_account

    def on_submit(self):
        self.make_gl_entries()

    def on_cancel(self):
        self.make_reverse_gl_entries()

    def make_gl_entries(self):
        if self.payment_type == "Receive":
            entries = [
                {"account": self.paid_to, "debit": self.received_amount, "credit": 0},
                {"account": self.paid_from, "debit": 0, "credit": self.paid_amount},
            ]
        elif self.payment_type == "Pay":
            entries = [
                {"account": self.paid_to, "debit": 0, "credit": self.received_amount},
                {"account": self.paid_from, "debit": self.paid_amount, "credit": 0},
            ]
        else:
            entries = [
                {"account": self.paid_from, "debit": 0, "credit": self.paid_amount},
                {"account": self.paid_to, "debit": self.received_amount, "credit": 0},
            ]

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
                "party_type": self.party_type,
                "party": self.party,
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


# Module-level hooks wrappers
def validate(doc, method):
    pass

def on_submit(doc, method):
    pass

def on_cancel(doc, method):
    pass
