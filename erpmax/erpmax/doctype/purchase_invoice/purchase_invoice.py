import frappe
from frappe.model.document import Document

class PurchaseInvoice(Document):
    def before_save(self):
        total_qty = total_amount = 0
        for row in self.get("items", []):
            row.amount = row.qty * row.rate
            total_qty += row.qty
            total_amount += row.amount
        self.total_qty = total_qty
        self.total_amount = total_amount
        paid = self.paid_amount or 0
        self.outstanding_amount = total_amount - paid

    def on_submit(self):
        self.status = "Paid" if self.outstanding_amount <= 0 else "Submitted"
