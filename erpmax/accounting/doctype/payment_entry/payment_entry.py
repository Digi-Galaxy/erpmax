import frappe
from frappe.model.document import Document
from erpmax.erpmax.doctype.journal_entry.journal_entry import flt


class PaymentEntry(Document):
    def validate(self):
        self.set_accounts()
        self.calculate_amounts()
        self.set_total_allocated()

    def on_submit(self):
        self.update_outstanding()

    def on_cancel(self):
        self.reverse_outstanding()

    def set_accounts(self):
        if self.payment_type == "Receive":
            if not self.paid_from:
                self.paid_from = self._get_default_receivable_account()
            if not self.paid_to:
                self.paid_to = self._get_default_cash_account()
        elif self.payment_type == "Pay":
            if not self.paid_from:
                self.paid_from = self._get_default_cash_account()
            if not self.paid_to:
                self.paid_to = self._get_default_payable_account()

    def calculate_amounts(self):
        self.base_paid_amount = flt(self.paid_amount)
        b = flt(self.received_amount) if self.received_amount else flt(self.paid_amount)
        self.base_received_amount = b
        if not self.received_amount:
            self.received_amount = self.paid_amount
        self.difference_amount = flt(self.paid_amount) - flt(self.total_allocated_amount)
        self.unallocated_amount = flt(self.paid_amount) - flt(self.total_allocated_amount)

    def set_total_allocated(self):
        total = 0.0
        for row in self.get("references", []):
            total += flt(row.allocated_amount)
        self.total_allocated_amount = total

    def update_outstanding(self):
        for row in self.get("references", []):
            if row.reference_doctype and row.reference_name:
                curr = frappe.db.get_value(
                    row.reference_doctype, row.reference_name, "outstanding_amount"
                )
                new_out = flt(curr) - flt(row.allocated_amount)
                frappe.db.set_value(
                    row.reference_doctype, row.reference_name,
                    "outstanding_amount", new_out
                )

    def reverse_outstanding(self):
        for row in self.get("references", []):
            if row.reference_doctype and row.reference_name:
                curr = frappe.db.get_value(
                    row.reference_doctype, row.reference_name, "outstanding_amount"
                )
                new_out = flt(curr) + flt(row.allocated_amount)
                frappe.db.set_value(
                    row.reference_doctype, row.reference_name,
                    "outstanding_amount", new_out
                )

    def _get_default_receivable_account(self):
        return frappe.db.get_value("Account", {
            "company": self.company, "account_type": "Receivable", "is_group": 0
        }, "name")

    def _get_default_payable_account(self):
        return frappe.db.get_value("Account", {
            "company": self.company, "account_type": "Payable", "is_group": 0
        }, "name")

    def _get_default_cash_account(self):
        return frappe.db.get_value("Account", {
            "company": self.company, "account_type": "Cash", "is_group": 0
        }, "name")

