import frappe
from frappe.model.document import Document

class Prospect(Document):
    def before_insert(self):
        if self.get("company_name"):
            self.name = self.company_name
