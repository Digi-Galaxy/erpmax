import frappe
from frappe.model.document import Document


class BankStatement(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_lines()

    def calculate_totals(self):
        self.total_debit = 0
        self.total_credit = 0
        self.total_transactions = len(self.lines or [])
        for line in self.lines:
            if line.transaction_type == "Debit":
                self.total_debit += line.amount or 0
            else:
                self.total_credit += line.amount or 0

    def validate_lines(self):
        if not self.lines:
            frappe.throw("At least one transaction line is required")
        for line in self.lines:
            if not line.date:
                frappe.throw(f"Row #{line.idx}: Date is required")
            if not line.description:
                frappe.throw(f"Row #{line.idx}: Description is required")

    def on_submit(self):
        self.status = "Submitted"
        self.update_bank_account_sync()
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_update()

    def update_bank_account_sync(self):
        if self.bank_account:
            frappe.db.set_value("Bank Account", self.bank_account, "last_sync_date", self.posting_date)

    @frappe.whitelist()
    def auto_reconcile(self):
        matched = 0
        for line in self.lines:
            if line.is_reconciled:
                continue

            payment = frappe.db.get_value("Payment Entry", {
                "paid_amount": line.amount,
                "posting_date": line.date,
                "docstatus": 1,
                "name": ["not in", self.get_reconciled_payments()],
            }, "name")

            if payment:
                line.payment_entry = payment
                line.is_reconciled = 1
                matched += 1

        self.save()
        return {"matched": matched, "total": len(self.lines)}

    def get_reconciled_payments(self):
        reconciled = []
        for line in self.lines:
            if line.payment_entry:
                reconciled.append(line.payment_entry)
        return reconciled
