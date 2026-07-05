# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def get_context(context):
    """Get context for settings page"""
    context.no_cache = 1
    context.title = _("ERPMax Settings")
    
    # Get current settings
    settings = frappe.get_single("ERPMax Settings")
    context.settings = settings
    
    # Get enabled modules
    from erpmax.utils.modules import get_enabled_modules
    context.enabled_modules = get_enabled_modules()
    
    # Get company info
    companies = frappe.get_all("Company", fields=["name", "company_name"])
    context.companies = companies
    
    return context


@frappe.whitelist()
def get_system_info():
    """Get system information"""
    return {
        "version": frappe.__version__,
        "site": frappe.local.site,
        "developer_mode": frappe.conf.developer_mode,
        "pending_migrations": frappe.db.sql("SELECT COUNT(*) FROM tabDocType WHERE module='ERPMax'")[0][0]
    }


@frappe.whitelist()
def get_module_status():
    """Get module status"""
    from erpmax.utils.modules import get_enabled_modules
    return get_enabled_modules()


@frappe.whitelist()
def clear_cache():
    """Clear cache"""
    frappe.clear_cache()
    return {"status": "Cache cleared"}


@frappe.whitelist()
def rebuild_assets():
    """Rebuild assets"""
    import subprocess
    import os
    
    bench_path = os.path.join(frappe.get_app_path("erpmax"), "..", "..")
    subprocess.run(["bench", "build", "--app", "erpmax"], cwd=bench_path)
    return {"status": "Assets rebuilt"}
