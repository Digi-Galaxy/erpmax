import frappe


def after_install():
    create_default_coa()


def create_default_coa():
    from erpmax.accounting.api.coa import onboard
    if frappe.db.exists("Account", {"account_name": "1000 Assets"}):
        return
    try:
        result = onboard("GAAP")
        frappe.logger().info(f"COA created: {result.get('total', 0)} accounts")
    except Exception as e:
        frappe.logger().info(f"COA deferred (company setup required): {e}")
