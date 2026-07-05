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

    rows = frappe.db.sql("""SELECT gl.account, a.account_type,
              SUM(gl.debit - gl.credit) AS balance
       FROM `tabGL Entry` gl
       LEFT JOIN `tabAccount` a ON a.name = gl.account
       WHERE {cond} AND a.account_type IN ('Bank', 'Cash')
       GROUP BY gl.account, a.account_type ORDER BY a.account_type, gl.account""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"account": r.account, "account_type": r.account_type,
        "balance": r.balance or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 260},
        {"label": _("Type"), "fieldname": "account_type", "fieldtype": "Data", "width": 100},
        {"label": _("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 150},
    ]