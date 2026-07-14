import frappe
from frappe.utils import nowdate


def after_install():
    """Post-install setup tasks."""
    create_default_coa()


def create_default_coa():
    """Create default Chart of Accounts if no company exists yet."""
    from erpmax.accounting.api.coa import onboard

    if frappe.db.exists("Account", {"account_name": "Assets"}):
        return

    company = frappe.db.get_single_value("System Settings", "company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    if not company:
        return

    try:
        onboard("GAAP")
        frappe.logger().info(f"Default GAAP COA created for {company}")
    except Exception as e:
        frappe.logger().error(f"COA creation skipped (no company yet): {e}")
