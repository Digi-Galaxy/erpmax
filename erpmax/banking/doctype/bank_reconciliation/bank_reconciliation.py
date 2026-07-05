import frappe
from frappe.model.document import Document


class BankReconciliation(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_items()

    def calculate_totals(self):
        self.total_reconciled = 0
        self.total_unreconciled = 0
        for item in self.items:
            if item.is_matched:
                self.total_reconciled += item.bank_amount or 0
            else:
                self.total_unreconciled += item.bank_amount or 0

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one reconciliation item is required")

    def on_submit(self):
        self.status = "Submitted"
        self.update_payment_entries()
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.reverse_payment_entries()
        self.db_update()

    def update_payment_entries(self):
        for item in self.items:
            if item.is_matched and item.payment_entry:
                frappe.db.set_value("Payment Entry", item.payment_entry, "cleared_date", self.reconciliation_date)

    def reverse_payment_entries(self):
        for item in self.items:
            if item.is_matched and item.payment_entry:
                frappe.db.set_value("Payment Entry", item.payment_entry, "cleared_date", None)

    @frappe.whitelist()
    def auto_match(self):
        matched = 0
        for item in self.items:
            if item.is_matched:
                continue

            payment = frappe.db.get_value("Payment Entry", {
                "paid_amount": item.bank_amount,
                "docstatus": 1,
                "cleared_date": ["is", "not set"],
            }, "name")

            if payment:
                item.payment_entry = payment
                item.is_matched = 1
                item.match_confidence = 100
                matched += 1

        self.save()
        return {"matched": matched, "total": len(self.items)}
