import frappe
from frappe.model.document import Document


class FiscalYear(Document):
    def validate(self):
        if not self.fiscal_year_name:
            self.fiscal_year_name = self.fiscal_year
        if not self.fiscal_year:
            self.fiscal_year = self.fiscal_year_name
