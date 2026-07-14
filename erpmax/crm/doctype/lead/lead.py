import frappe
from frappe.model.document import Document

class Lead(Document):
    def before_insert(self):
        if self.get("lead_name"):
            self.name = self.lead_name
