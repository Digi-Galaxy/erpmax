import frappe
from frappe import _

@frappe.whitelist()
def test_fuzzy_match(text, doctype="Customer"):
    return {"text": text, "doctype": doctype, "match": True}

@frappe.whitelist()
def get_matching_suggestions(text, doctype="Customer", limit=10):
    results = frappe.get_all(doctype, fields=["name", "customer_name" if doctype == "Customer" else "supplier_name"], limit=limit)
    return results
