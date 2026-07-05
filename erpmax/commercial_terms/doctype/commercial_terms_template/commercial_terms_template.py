import frappe
from frappe.model.document import Document

class CommercialTermsTemplate(Document):
    def validate(self):
        if not self.rules:
            frappe.throw("At least one rule is required")
