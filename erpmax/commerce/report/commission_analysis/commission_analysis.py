from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = []
    params = {}
    
    if filters.get("agent"):
        cond.append("cl.agent = %(agent)s")
        params["agent"] = filters["agent"]
    if filters.get("from_date"):
        cond.append("cl.posting_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond.append("cl.posting_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]
    if filters.get("status"):
        cond.append("cl.status = %(status)s")
        params["status"] = filters["status"]
    
    where = " AND ".join(cond) if cond else "1=1"
    
    rows = frappe.db.sql("""SELECT 
            cl.agent,
            ROUND(SUM(CASE WHEN cl.status = "Accrued" THEN cl.commission_amount ELSE 0 END), 2) AS total_accrued,
            ROUND(SUM(CASE WHEN cl.status = "Paid" THEN cl.commission_amount ELSE 0 END), 2) AS total_paid,
            ROUND(SUM(CASE WHEN cl.status = "Recovered" THEN ABS(cl.commission_amount) ELSE 0 END), 2) AS total_recovered,
            ROUND(SUM(CASE WHEN cl.status = "Cancelled" THEN ABS(cl.commission_amount) ELSE 0 END), 2) AS total_cancelled,
            COUNT(CASE WHEN cl.status = "Accrued" THEN 1 END) AS pending_invoices,
            MAX(CASE WHEN cl.status = "Accrued" THEN cl.posting_date END) AS last_invoice_date
        FROM `tabCommission Ledger` cl
        WHERE cl.docstatus < 2 AND {where}
        GROUP BY cl.agent
        ORDER BY total_accrued DESC
    """.format(where=where), params, as_dict=True)
    
    data = []
    for r in rows:
        net_outstanding = (r.total_accrued or 0) - (r.total_recovered or 0)
        data.append({
            "agent": r.agent,
            "total_accrued": r.total_accrued or 0,
            "total_paid": r.total_paid or 0,
            "total_recovered": r.total_recovered or 0,
            "total_cancelled": r.total_cancelled or 0,
            "net_outstanding": net_outstanding,
            "pending_invoices": r.pending_invoices or 0,
            "last_invoice_date": r.last_invoice_date,
        })
    
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Link", "options": "Sales Agent", "width": 200},
        {"label": _("Total Accrued"), "fieldname": "total_accrued", "fieldtype": "Currency", "width": 140},
        {"label": _("Total Paid"), "fieldname": "total_paid", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Recovered"), "fieldname": "total_recovered", "fieldtype": "Currency", "width": 140},
        {"label": _("Total Cancelled"), "fieldname": "total_cancelled", "fieldtype": "Currency", "width": 140},
        {"label": _("Net Outstanding"), "fieldname": "net_outstanding", "fieldtype": "Currency", "width": 150},
        {"label": _("Pending Invoices"), "fieldname": "pending_invoices", "fieldtype": "Int", "width": 130},
        {"label": _("Last Invoice Date"), "fieldname": "last_invoice_date", "fieldtype": "Date", "width": 140},
    ]
