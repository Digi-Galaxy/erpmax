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

    rows = frappe.db.sql("""SELECT gl.account AS bank_account,
              SUM(gl.debit - gl.credit) AS balance
       FROM `tabGL Entry` gl
       LEFT JOIN `tabAccount` a ON a.name = gl.account
       WHERE {cond} AND a.account_type = 'Bank'
       GROUP BY gl.account ORDER BY gl.account""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"bank_account": r.bank_account, "balance": r.balance or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Bank Account"), "fieldname": "bank_account", "fieldtype": "Link", "options": "Account", "width": 260},
        {"label": _("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 150},
    ]