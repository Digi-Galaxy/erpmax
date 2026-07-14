import frappe
from frappe.model.document import Document


class ExchangeRate(Document):
    def validate(self):
        self.validate_rate()

    def validate_rate(self):
        if self.rate and self.rate <= 0:
            frappe.throw("Exchange Rate must be greater than zero")
