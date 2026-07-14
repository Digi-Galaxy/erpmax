import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class EHSigningCertificate(Document):
    def validate(self):
        if self.valid_to and self.valid_to < nowdate():
            self.status = "Expired"

    def before_save(self):
        self.status = "Active"

    def on_update(self):
        if self.is_active:
            frappe.db.set_value(
                "EH Signing Certificate",
                {"is_active": 1, "name": ["!=", self.name]},
                "is_active",
                0,
            )
