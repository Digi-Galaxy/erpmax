import frappe
from frappe.model.document import Document

class CommercialTermsTemplate(Document):
    def validate(self):
        if not self.rules:
            frappe.throw("At least one rule is required")
        for i, rule in enumerate(self.rules):
            if not rule.effect:
                frappe.throw("Row %d: Effect is required" % (i + 1))
            if not rule.direction:
                frappe.throw("Row %d: Direction is required" % (i + 1))
