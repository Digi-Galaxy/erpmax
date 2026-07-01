import frappe
from frappe.model.document import Document


class EHSettings(Document):
    def validate(self):
        if self.default_country_profile:
            profile = frappe.get_doc("EH Country Profile", self.default_country_profile)
            if not profile.is_default:
                profile.is_default = 1
                profile.save()
