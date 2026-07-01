import frappe
from frappe.model.document import Document

class CostCentre(Document):
    def before_save(self):
        if not self.cost_centre_name:
            self.cost_centre_name = self.name
