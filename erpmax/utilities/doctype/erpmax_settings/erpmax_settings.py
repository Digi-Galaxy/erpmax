import frappe
from frappe.model.document import Document


class ERPMaxSettings(Document):
    def validate(self):
        self.validate_module_dependencies()

    def validate_module_dependencies(self):
        if self.enable_sales and not self.enable_accounts:
            frappe.throw("Sales module requires Accounts module to be enabled")

        if self.enable_purchase and not self.enable_accounts:
            frappe.throw("Purchase module requires Accounts module to be enabled")

        if self.enable_inventory and not self.enable_accounts:
            frappe.throw("Inventory module requires Accounts module to be enabled")

        if self.enable_projects and not self.enable_accounts:
            frappe.throw("Projects module requires Accounts module to be enabled")

        if self.enable_expenses and not self.enable_accounts:
            frappe.throw("Expenses module requires Accounts module to be enabled")

        if self.enable_partner_finance and not self.enable_accounts:
            frappe.throw("Partner Finance module requires Accounts module to be enabled")

        if self.enable_transport and not self.enable_sales:
            frappe.throw("Transport module requires Sales module to be enabled")

        if self.enable_commission and not self.enable_sales:
            frappe.throw("Commission module requires Sales module to be enabled")

        if self.enable_recurring and not self.enable_sales:
            frappe.throw("Recurring module requires Sales module to be enabled")

    def is_module_enabled(self, module_name):
        field_name = f"enable_{module_name.lower().replace(' ', '_')}"
        return getattr(self, field_name, 0) == 1

    def get_enabled_modules(self):
        modules = []
        for field in self.meta.fields:
            if field.fieldname and field.fieldname.startswith("enable_"):
                if getattr(self, field.fieldname, 0) == 1:
                    modules.append(field.fieldname.replace("enable_", ""))
        return modules

    def get_disabled_modules(self):
        modules = []
        for field in self.meta.fields:
            if field.fieldname and field.fieldname.startswith("enable_"):
                if getattr(self, field.fieldname, 0) == 0:
                    modules.append(field.fieldname.replace("enable_", ""))
        return modules
