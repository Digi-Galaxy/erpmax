import frappe
from frappe.model.document import Document

class Project(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw("End date cannot be before start date")

