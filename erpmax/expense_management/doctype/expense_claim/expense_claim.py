import frappe
from frappe.model.document import Document

class ExpenseClaim(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        self.total_amount = sum((row.amount or 0) for row in self.expenses)
        self.approved_amount = sum((row.approved_amount or 0) for row in self.expenses if row.approved_amount)
    def on_submit(self):
        self.status = "Approved"
    def on_cancel(self):
        self.status = "Rejected"

