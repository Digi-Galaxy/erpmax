import frappe
from frappe.model.document import Document
import re


class ReconciliationRule(Document):
    def validate(self):
        self.validate_rule()

    def validate_rule(self):
        if not self.match_field:
            frappe.throw("Match field is required")
        if not self.action_type:
            frappe.throw("Action type is required")

    @frappe.whitelist()
    def test_rule(self, test_description):
        if self.match_type == "Contains":
            return test_description.lower().find(self.match_value.lower()) >= 0
        elif self.match_type == "Starts With":
            return test_description.lower().startswith(self.match_value.lower())
        elif self.match_type == "Ends With":
            return test_description.lower().endswith(self.match_value.lower())
        elif self.match_type == "Regex":
            return bool(re.search(self.match_value, test_description))
        elif self.match_type == "Exact":
            return test_description.lower() == self.match_value.lower()
        return False
