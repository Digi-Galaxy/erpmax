import frappe


@frappe.whitelist()
def get_count(doctype, filters=None, debug=False):
    """Override frappe.client.get_count"""
    return frappe.db.count(doctype, filters=filters, debug=debug)
