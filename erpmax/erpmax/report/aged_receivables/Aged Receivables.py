import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1", "outstanding_amount > 0"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("customer"):
        cond.append("customer=%(customer)s")
        params["customer"] = filters["customer"]
    if filters.get("to_date"):
        cond.append("posting_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    rows = frappe.db.sql("""SELECT customer, name AS invoice, posting_date, due_date,
              outstanding_amount,
              DATEDIFF(CURDATE(), due_date) AS overdue_days
       FROM `tabSales Invoice`
       WHERE {cond}
       ORDER BY due_date ASC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"customer": r.customer, "invoice": r.invoice, "posting_date": r.posting_date,
        "due_date": r.due_date, "outstanding": r.outstanding_amount or 0,
        "overdue_days": r.overdue_days or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 180},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 110},
        {"label": _("Outstanding"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 140},
        {"label": _("Overdue Days"), "fieldname": "overdue_days", "fieldtype": "Int", "width": 100},
    ]