import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT posting_date, payment_type, party_type, party,
              mode_of_payment, paid_amount, base_paid_amount, reference_no, reference_date
       FROM `tabPayment Entry`
       WHERE {cond} ORDER BY posting_date DESC""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"posting_date": r.posting_date, "payment_type": r.payment_type,
        "party": r.party, "mode_of_payment": r.mode_of_payment,
        "amount": r.base_paid_amount or 0, "reference_no": r.reference_no} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Type"), "fieldname": "payment_type", "fieldtype": "Data", "width": 100},
        {"label": _("Party"), "fieldname": "party", "fieldtype": "Dynamic Link", "options": "party_type", "width": 200},
        {"label": _("Mode"), "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 120},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Ref No"), "fieldname": "reference_no", "fieldtype": "Data", "width": 150},
    ]