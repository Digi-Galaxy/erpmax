import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class Budget(Document):
    def validate(self):
        self.validate_dates()
        self.validate_year()

    def validate_dates(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw(_("From Date must be before To Date"))

    def validate_year(self):
        if self.fiscal_year:
            year = frappe.get_cached_doc("Fiscal Year", self.fiscal_year)
            if self.from_date and self.from_date < year.start_date:
                frappe.throw(_("From Date cannot be before Fiscal Year start"))
            if self.to_date and self.to_date > year.end_date:
                frappe.throw(_("To Date cannot be after Fiscal Year end"))
