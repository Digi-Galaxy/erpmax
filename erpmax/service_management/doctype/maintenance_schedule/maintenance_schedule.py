import frappe
from frappe.model.document import Document
from erpmax.service_management.utils.flow import set_stage, get_allowed_stages


class MaintenanceSchedule(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        if self.customer and not self.customer_name:
            self.customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")
        if not self.current_stage:
            self.current_stage = "Draft"

    @frappe.whitelist()
    def set_stage(self, to_stage, notes=None):
        set_stage(self, to_stage, notes=notes)
        return {"current_stage": self.current_stage}

    @frappe.whitelist()
    def get_allowed_stages(self):
        return get_allowed_stages(self.doctype, self.current_stage)

    @frappe.whitelist()
    def generate_pdf(self):
        from erpmax.service_management.utils.pdf_contract import generate_contract_pdf
        return generate_contract_pdf(self.doctype, self.name)
