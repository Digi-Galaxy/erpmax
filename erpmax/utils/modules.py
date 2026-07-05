import frappe


def is_module_enabled(module_name):
    try:
        settings = frappe.get_single("ERPMax Settings")
        field_name = f"enable_{module_name.lower().replace(' ', '_')}"
        return getattr(settings, field_name, 0) == 1
    except Exception:
        return True


def get_enabled_modules():
    try:
        settings = frappe.get_single("ERPMax Settings")
        modules = []
        for field in settings.meta.fields:
            if field.fieldname and field.fieldname.startswith("enable_"):
                if getattr(settings, field.fieldname, 0) == 1:
                    modules.append(field.fieldname.replace("enable_", ""))
        return modules
    except Exception:
        return ["accounts", "company", "fiscal_year", "sales", "quotation",
                "sales_order", "proforma", "recurring", "commission",
                "purchase", "supplier_quotation", "purchase_order",
                "partner_finance", "internal_transfer", "transport",
                "expenses", "projects", "reporting", "dashboard",
                "compliance", "api", "printing"]


def get_disabled_modules():
    try:
        settings = frappe.get_single("ERPMax Settings")
        modules = []
        for field in settings.meta.fields:
            if field.fieldname and field.fieldname.startswith("enable_"):
                if getattr(settings, field.fieldname, 0) == 0:
                    modules.append(field.fieldname.replace("enable_", ""))
        return modules
    except Exception:
        return []


def require_module(module_name):
    if not is_module_enabled(module_name):
        frappe.throw(
            f"The {module_name} module is not enabled. "
            f"Please enable it in ERPMax Settings."
        )
