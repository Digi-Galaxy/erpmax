import frappe
from frappe.model.document import Document

class Opportunity(Document):
    def validate(self):
        if self.status in ("Won", "Lost") and not self.expected_close_date:
            frappe.msgprint(f"Setting expected close date to today for {self.status} opportunity")
            self.expected_close_date = frappe.utils.today()
