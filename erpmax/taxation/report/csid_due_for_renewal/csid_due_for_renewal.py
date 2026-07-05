import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, None


def get_columns():
    return [
        {"fieldname": "company", "fieldtype": "Link", "label": _("Company"), "options": "Company", "width": 180},
        {"fieldname": "name", "fieldtype": "Link", "label": _("CSID"), "options": "Zatca Csid", "width": 180},
        {"fieldname": "csid_type", "fieldtype": "Data", "label": _("CSID Type"), "width": 120},
        {"fieldname": "expiry_date", "fieldtype": "Date", "label": _("Expiry Date"), "width": 110},
        {"fieldname": "days_left", "fieldtype": "Int", "label": _("Days Left"), "width": 90},
        {"fieldname": "status", "fieldtype": "Data", "label": _("Status"), "width": 100},
    ]


def get_data(filters):
    today = getdate(nowdate())
    renewal_window_days = frappe.utils.cint(filters.get("renewal_window_days") or 30)
    company = filters.get("company")
    csid_type = filters.get("csid_type")
    include_expired = frappe.utils.cint(filters.get("include_expired") or 0)

    query_filters = {"expiry_date": ["is", "set"]}
    if company:
        query_filters["company"] = company
    if csid_type:
        query_filters["csid_type"] = csid_type

    records = frappe.get_all(
        "Zatca Csid",
        fields=["name", "company", "csid_type", "expiry_date", "status"],
        filters=query_filters,
        order_by="expiry_date asc",
    )

    data = []
    for row in records:
        expiry_date = getdate(row.expiry_date)
        days_left = (expiry_date - today).days
        if days_left > renewal_window_days:
            continue
        if days_left < 0 and not include_expired:
            continue
        data.append({
            "company": row.company,
            "name": row.name,
            "csid_type": row.csid_type,
            "expiry_date": row.expiry_date,
            "days_left": days_left,
            "status": row.status or ("Expired" if days_left < 0 else "Active"),
        })

    return data
