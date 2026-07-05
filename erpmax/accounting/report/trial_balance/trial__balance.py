import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["gl.is_cancelled = 0"]
    params = {}
    if filters.get("company"):
        cond.append("gl.company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("to_date"):
        cond.append("gl.posting_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    rows = frappe.db.sql("""SELECT gl.account, a.root_type,
              SUM(gl.debit - gl.credit) AS balance
       FROM `tabGL Entry` gl
       LEFT JOIN `tabAccount` a ON a.name = gl.account
       WHERE {cond} GROUP BY gl.account, a.root_type
       ORDER BY a.root_type, gl.account""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = []
    totals = {"debit": 0, "credit": 0}
    for r in rows:
        bal = r.balance or 0
        if r.root_type in ("Asset", "Expense"):
            dr = abs(bal) if bal > 0 else 0
            cr = abs(bal) if bal < 0 else 0
        else:
            cr = bal if bal > 0 else 0
            dr = abs(bal) if bal < 0 else 0
        totals["debit"] += dr
        totals["credit"] += cr
        data.append({"account": r.account, "root_type": r.root_type, "debit": dr, "credit": cr})
    data.append({"account": "<b>Total</b>", "root_type": "", "debit": totals["debit"], "credit": totals["credit"]})
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 260},
        {"label": _("Type"), "fieldname": "root_type", "fieldtype": "Data", "width": 100},
        {"label": _("Debit"), "fieldname": "debit", "fieldtype": "Currency", "width": 140},
        {"label": _("Credit"), "fieldname": "credit", "fieldtype": "Currency", "width": 140},
    ]