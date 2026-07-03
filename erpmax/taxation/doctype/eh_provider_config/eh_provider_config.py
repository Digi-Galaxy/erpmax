import frappe
from frappe.model.document import Document


class EHProviderConfig(Document):
    def on_update(self):
        self.update_company_profile()

    def update_company_profile(self):
        if self.company:
            company = frappe.get_doc("Company", self.company)
            company.db_set("eh_provider_config", self.name)
