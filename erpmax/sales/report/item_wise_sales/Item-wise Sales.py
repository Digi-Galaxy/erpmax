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
    if filters.get("item_code"):
        cond.append("sii.item_code=%(item_code)s")
        params["item_code"] = filters["item_code"]

    rows = frappe.db.sql("""SELECT sii.item_code AS item,
              i.item_name, SUM(sii.qty) AS qty,
              SUM(sii.base_net_amount) AS amount,
              SUM(sii.base_rate) / COUNT(*) AS avg_rate,
              COUNT(DISTINCT si.name) AS invoice_count
       FROM `tabSales Invoice Item` sii
       INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
       LEFT JOIN `tabItem` i ON i.name = sii.item_code
       WHERE {cond} GROUP BY sii.item_code, i.item_name ORDER BY amount DESC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"item": r.item, "item_name": r.item_name, "qty": r.qty or 0,
        "amount": r.amount or 0, "avg_rate": r.avg_rate or 0, "invoice_count": r.invoice_count or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Avg Rate"), "fieldname": "avg_rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 100},
    ]