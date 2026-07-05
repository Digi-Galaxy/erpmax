import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("customer"):
        cond.append("customer=%(customer)s")
        params["customer"] = filters["customer"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT name, customer, posting_date, due_date,
              base_grand_total, paid_amount, outstanding_amount, status
       FROM `tabSales Invoice`
       WHERE {cond} ORDER BY customer, posting_date""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"name": r.name, "customer": r.customer, "posting_date": r.posting_date,
        "due_date": r.due_date, "grand_total": r.base_grand_total or 0,
        "paid": r.paid_amount or 0, "outstanding": r.outstanding_amount or 0,
        "status": r.status} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 180},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 130},
        {"label": _("Paid"), "fieldname": "paid", "fieldtype": "Currency", "width": 130},
        {"label": _("Outstanding"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 130},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]