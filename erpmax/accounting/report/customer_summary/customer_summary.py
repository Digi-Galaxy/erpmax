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

    rows = frappe.db.sql("""SELECT customer,
              SUM(grand_total) AS billed,
              SUM(grand_total - outstanding_amount) AS paid,
              SUM(outstanding_amount) AS outstanding
       FROM `tabSales Invoice`
       WHERE {cond}
       GROUP BY customer
       ORDER BY customer""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"customer": r.customer, "billed": r.billed or 0,
        "paid": r.paid or 0, "outstanding": r.outstanding or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 260},
        {"label": _("Billed"), "fieldname": "billed", "fieldtype": "Currency", "width": 140},
        {"label": _("Paid"), "fieldname": "paid", "fieldtype": "Currency", "width": 140},
        {"label": _("Outstanding"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 170},
    ]