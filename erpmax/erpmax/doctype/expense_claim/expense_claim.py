import frappe
from frappe.model.document import Document

class ExpenseClaim(Document):
    def before_save(self):
        total = 0
        for row in self.get("expenses", []):
            total += row.amount
        self.total_amount = total

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Draft"
