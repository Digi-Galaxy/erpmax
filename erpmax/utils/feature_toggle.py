import frappe

@frappe.whitelist(allow_guest=False)
def get_feature_toggles(company=None):
    settings = frappe.get_cached_doc("ERPMax Settings")
    toggles = {}
    for field in settings.meta.fields:
        if field.fieldname.startswith("fea_"):
            toggles[field.fieldname] = settings.get(field.fieldname, 0)
    toggles["enable_commercial_terms"] = settings.get("enable_commercial_terms", 0)
    return toggles

def is_enabled(feature_key, company=None):
    settings = frappe.get_cached_doc("ERPMax Settings")
    return bool(settings.get(f"fea_{feature_key}", 0))

def is_commercial_terms_enabled(company=None):
    settings = frappe.get_cached_doc("ERPMax Settings")
    return bool(settings.get("enable_commercial_terms", 0))
