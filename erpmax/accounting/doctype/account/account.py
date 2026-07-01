import frappe
from frappe.model.document import Document

class Account(Document):
    def before_save(self):
        if self.is_group:
            self.account_type = ""
        if not self.account_currency:
            self.account_currency = frappe.db.get_value("Company", self.get("company"), "default_currency") or "SAR"

    def on_trash(self):
        if frappe.db.exists("Account", {"parent_account": self.name}):
            frappe.throw("Cannot delete account with child accounts")

    def autoname(self):
        if self.account_name and not self.name:
            self.name = self.account_name
