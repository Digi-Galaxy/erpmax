import frappe
from frappe.model.document import Document

class Account(Document):
    def before_save(self):
        if self.is_group:
            self.account_type = ""
