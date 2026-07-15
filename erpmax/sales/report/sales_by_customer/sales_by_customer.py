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
              SUM(total) AS net_sales,
              SUM(grand_total) AS grand_total,
              COUNT(name) AS invoice_count
       FROM `tabSales Invoice`
       WHERE {cond} GROUP BY customer ORDER BY grand_total DESC LIMIT 50""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"customer": r.customer, "net_sales": r.net_sales or 0,
        "grand_total": r.grand_total or 0, "invoice_count": r.invoice_count or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 260},
        {"label": _("Net Sales"), "fieldname": "net_sales", "fieldtype": "Currency", "width": 140},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 100},
    ]
