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

    rows = frappe.db.sql("""SELECT gl.account, a.root_type, a.account_type,
              SUM(gl.debit - gl.credit) AS balance
       FROM `tabGL Entry` gl
       LEFT JOIN `tabAccount` a ON a.name = gl.account
       WHERE {cond} AND a.root_type IN ('Asset', 'Liability', 'Equity')
       GROUP BY gl.account, a.root_type, a.account_type
       ORDER BY a.root_type, gl.account""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    assets = []
    liabilities = []
    equity = []
    asset_total = 0
    liability_total = 0
    equity_total = 0
    for r in rows:
        bal = r.balance or 0
        if r.root_type == "Asset":
            assets.append({"account": r.account, "amount": abs(bal)})
            asset_total += abs(bal)
        elif r.root_type == "Liability":
            liabilities.append({"account": r.account, "amount": abs(bal)})
            liability_total += abs(bal)
        else:
            equity.append({"account": r.account, "amount": abs(bal)})
            equity_total += abs(bal)
    data = [{"account": "<b>ASSETS</b>", "amount": 0}] + assets
    data += [{"account": "<b>Total Assets</b>", "amount": asset_total}]
    data += [{"account": "", "amount": 0}]
    data += [{"account": "<b>LIABILITIES</b>", "amount": 0}] + liabilities
    data += [{"account": "<b>Total Liabilities</b>", "amount": liability_total}]
    data += [{"account": "", "amount": 0}]
    data += [{"account": "<b>EQUITY</b>", "amount": 0}] + equity
    data += [{"account": "<b>Total Equity</b>", "amount": equity_total}]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Data", "width": 350},
        {"label": _("Balance"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
    ]