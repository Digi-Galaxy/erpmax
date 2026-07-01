import frappe
from frappe.model.document import Document

class PurchaseOrder(Document):
    def before_save(self):
        total_qty = total_amount = 0
        for row in self.get("items", []):
            row.amount = row.qty * row.rate
            total_qty += row.qty
            total_amount += row.amount
        self.total_qty = total_qty
        self.total_amount = total_amount

    def on_submit(self):
        self.status = "To Receive and Bill"
