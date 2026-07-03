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
    if filters.get("account"):
        cond.append("gl.account=%(account)s")
        params["account"] = filters["account"]
    if filters.get("voucher_type"):
        cond.append("gl.voucher_type=%(voucher_type)s")
        params["voucher_type"] = filters["voucher_type"]

    rows = frappe.db.sql("""SELECT gl.posting_date, gl.account,
              gl.voucher_type, gl.voucher_no,
              gl.debit, gl.credit, gl.against, gl.remarks
       FROM `tabGL Entry` gl
       WHERE {cond}
       ORDER BY gl.posting_date, gl.creation""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"posting_date": r.posting_date, "account": r.account,
        "voucher_type": r.voucher_type, "voucher_no": r.voucher_no,
        "debit": r.debit or 0, "credit": r.credit or 0,
        "against": r.against, "remarks": r.remarks} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"label": _("Voucher Type"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 150},
        {"label": _("Voucher No"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 180},
        {"label": _("Debit"), "fieldname": "debit", "fieldtype": "Currency", "width": 130},
        {"label": _("Credit"), "fieldname": "credit", "fieldtype": "Currency", "width": 130},
        {"label": _("Against"), "fieldname": "against", "fieldtype": "Data", "width": 150},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
    ]