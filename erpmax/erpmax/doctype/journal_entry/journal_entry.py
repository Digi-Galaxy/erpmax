import frappe
from frappe import _
from frappe.model.document import Document


def flt(val, precision=2):
    if val is None:
        return 0.0
    return round(float(val), precision)


class JournalEntry(Document):
    def validate(self):
        self.set_totals()
        self.validate_balance()

    def on_submit(self):
        self.set_as_posted()

    def on_cancel(self):
        self.set_as_cancelled()

    def set_totals(self):
        total_debit = 0.0
        total_credit = 0.0
        for row in self.get("accounts", []):
            total_debit += flt(row.debit)
            total_credit += flt(row.credit)
        self.total_debit = total_debit
        self.total_credit = total_credit
        self.difference = total_debit - total_credit

    def validate_balance(self):
        if abs(self.difference) > 0.01:
            frappe.throw(_("Total Debit ({0}) must equal Total Credit ({1})").format(
                self.total_debit, self.total_credit
            ))

    def set_as_posted(self):
        for row in self.get("accounts", []):
            frappe.db.sql("""
                UPDATE `tabAccount`
                SET current_balance = current_balance + %s - %s
                WHERE name = %s
            """, (flt(row.debit), flt(row.credit), row.account))

    def set_as_cancelled(self):
        for row in self.get("accounts", []):
            frappe.db.sql("""
                UPDATE `tabAccount`
                SET current_balance = current_balance - %s + %s
                WHERE name = %s
            """, (flt(row.debit), flt(row.credit), row.account))

