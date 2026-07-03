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

    rows = frappe.db.sql("""SELECT COUNT(name) AS invoice_count,
              SUM(base_grand_total) AS total_amount,
              SUM(base_total_taxes_and_charges) AS total_tax,
              SUM(net_total) AS net_total,
              SUM(outstanding_amount) AS total_outstanding
       FROM `tabSales Invoice`
       WHERE {cond}""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"invoice_count": r.invoice_count or 0, "net_total": r.net_total or 0,
        "total_tax": r.total_tax or 0, "total_amount": r.total_amount or 0,
        "total_outstanding": r.total_outstanding or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Invoice Count"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 130},
        {"label": _("Net Total"), "fieldname": "net_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Total Tax"), "fieldname": "total_tax", "fieldtype": "Currency", "width": 140},
        {"label": _("Grand Total"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Outstanding"), "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 140},
    ]