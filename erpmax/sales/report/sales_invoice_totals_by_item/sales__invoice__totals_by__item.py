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

    rows = frappe.db.sql("""SELECT sii.item_code AS item,
              SUM(sii.qty) AS total_qty,
              SUM(sii.base_net_amount) AS total_amount
       FROM `tabSales Invoice Item` sii
       INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
       WHERE {cond} GROUP BY sii.item_code ORDER BY total_amount DESC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"item": r.item, "total_qty": r.total_qty or 0,
        "total_amount": r.total_amount or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 260},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 110},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
    ]