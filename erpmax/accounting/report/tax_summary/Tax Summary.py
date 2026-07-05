import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["si.docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("si.company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT sit.account_head, sit.charge_type,
              SUM(sit.tax_amount) AS total_tax,
              COUNT(DISTINCT si.name) AS invoice_count
       FROM `tabSales Invoice Tax` sit
       INNER JOIN `tabSales Invoice` si ON si.name = sit.parent
       WHERE {cond} GROUP BY sit.account_head, sit.charge_type ORDER BY total_tax DESC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"account_head": r.account_head, "charge_type": r.charge_type,
        "total_tax": r.total_tax or 0, "invoice_count": r.invoice_count or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Tax Account"), "fieldname": "account_head", "fieldtype": "Link", "options": "Account", "width": 250},
        {"label": _("Charge Type"), "fieldname": "charge_type", "fieldtype": "Data", "width": 120},
        {"label": _("Total Tax"), "fieldname": "total_tax", "fieldtype": "Currency", "width": 140},
        {"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 100},
    ]