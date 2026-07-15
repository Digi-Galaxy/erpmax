import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT customer,
              COUNT(name) AS invoice_count,
              SUM(grand_total) AS total_amount,
              SUM(outstanding_amount) AS total_outstanding
       FROM `tabSales Invoice`
       WHERE {cond} GROUP BY customer ORDER BY total_amount DESC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"customer": r.customer, "invoice_count": r.invoice_count or 0,
        "total_amount": r.total_amount or 0, "total_outstanding": r.total_outstanding or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 260},
        {"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 100},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Outstanding"), "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 150},
    ]
