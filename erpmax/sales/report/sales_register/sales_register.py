import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "posting_date", "fieldtype": "Date", "label": _("Date"), "width": 100},
        {"fieldname": "name", "fieldtype": "Link", "label": _("Invoice"), "options": "Sales Invoice", "width": 150},
        {"fieldname": "customer_name", "fieldtype": "Data", "label": _("Customer"), "width": 200},
        {"fieldname": "grand_total", "fieldtype": "Currency", "label": _("Grand Total"), "width": 120},
    ]

def get_data(filters):
    si_filters = {"docstatus": 1}
    if filters and filters.get("from_date"):
        si_filters["posting_date"] = ["between", [filters["from_date"], filters.get("to_date", frappe.utils.nowdate())]]
    invoices = frappe.get_all("Sales Invoice", filters=si_filters, fields=["name", "posting_date", "customer_name", "grand_total"], order_by="posting_date desc")
    return invoices
