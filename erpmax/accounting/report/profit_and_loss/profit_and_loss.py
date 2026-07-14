import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["gl.is_cancelled = 0"]
    params = {}
    if filters.get("company"):
        cond.append("gl.company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("gl.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT gl.account, a.root_type, a.account_type,
              SUM(gl.debit - gl.credit) AS balance
       FROM `tabGL Entry` gl
       LEFT JOIN `tabAccount` a ON a.name = gl.account
       WHERE {cond} AND a.root_type IN ('Income', 'Expense')
       GROUP BY gl.account, a.root_type, a.account_type
       ORDER BY a.root_type, gl.account""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    income = []
    expense = []
    income_total = 0
    expense_total = 0
    for r in rows:
        bal = r.balance or 0
        if r.root_type == "Income":
            income.append({"account": r.account, "amount": abs(bal)})
            income_total += abs(bal)
        else:
            expense.append({"account": r.account, "amount": abs(bal)})
            expense_total += abs(bal)
    data = income + [{"account": "<b>Total Income</b>", "amount": income_total}]
    data += [{"account": "", "amount": 0}] + expense
    data += [{"account": "<b>Total Expense</b>", "amount": expense_total}]
    net = income_total - expense_total
    data += [{"account": "<b>Net Profit/Loss</b>", "amount": net}]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Data", "width": 300},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
    ]