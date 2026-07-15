# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_days


def execute(filters=None):
    """Customer Statement Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "label": _("Date"),
            "width": 100,
        },
        {
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "label": _("Voucher Type"),
            "width": 120,
        },
        {
            "fieldname": "voucher_no",
            "fieldtype": "Data",
            "label": _("Voucher No"),
            "width": 150,
        },
        {
            "fieldname": "debit",
            "fieldtype": "Currency",
            "label": _("Debit"),
            "width": 120,
        },
        {
            "fieldname": "credit",
            "fieldtype": "Currency",
            "label": _("Credit"),
            "width": 120,
        },
        {
            "fieldname": "balance",
            "fieldtype": "Currency",
            "label": _("Balance"),
            "width": 120,
        },
    ]


def get_data(filters):
    """Get customer statement data"""
    customer = filters.get("customer")
    from_date = filters.get("from_date") or add_days(getdate(), -365)
    to_date = filters.get("to_date") or getdate()
    company = filters.get("company")
    
    if not customer:
        frappe.throw(_("Customer is required"))
    
    # Get opening balance
    opening_balance = get_opening_balance(customer, from_date, company)
    
    # Get all transactions
    transactions = get_customer_transactions(customer, from_date, to_date, company)
    
    # Calculate running balance
    data = []
    running_balance = opening_balance
    
    for txn in transactions:
        running_balance += flt(txn.debit) - flt(txn.credit)
        
        data.append({
            "posting_date": txn.posting_date,
            "voucher_type": txn.voucher_type,
            "voucher_no": txn.voucher_no,
            "debit": flt(txn.debit, 2),
            "credit": flt(txn.credit, 2),
            "balance": flt(running_balance, 2),
        })
    
    # Add opening balance row
    data.insert(0, {
        "posting_date": add_days(getdate(from_date), -1),
        "voucher_type": "",
        "voucher_no": _("Opening Balance"),
        "debit": 0,
        "credit": 0,
        "balance": flt(opening_balance, 2),
    })
    
    # Add closing balance
    data.append({
        "posting_date": getdate(to_date),
        "voucher_type": "",
        "voucher_no": _("Closing Balance"),
        "debit": sum(d.get("debit", 0) for d in data[1:]),
        "credit": sum(d.get("credit", 0) for d in data[1:]),
        "balance": flt(running_balance, 2),
    })
    
    return data


def get_opening_balance(customer, from_date, company):
    """Get opening balance for customer"""
    filters = {
        "party_type": "Customer",
        "party": customer,
        "posting_date": ["<", from_date],
        "is_cancelled": 0,
    }
    
    if company:
        filters["company"] = company
    
    gl_entries = frappe.get_all(
        "GL Entry",
        filters=filters,
        fields=["debit", "credit"]
    )
    
    total_debit = sum(flt(entry.debit) for entry in gl_entries)
    total_credit = sum(flt(entry.credit) for entry in gl_entries)
    
    return total_debit - total_credit


def get_customer_transactions(customer, from_date, to_date, company):
    """Get all transactions for a customer"""
    filters = {
        "party_type": "Customer",
        "party": customer,
        "posting_date": ["between", [from_date, to_date]],
        "is_cancelled": 0,
    }
    
    if company:
        filters["company"] = company
    
    return frappe.get_all(
        "GL Entry",
        filters=filters,
        fields=["posting_date", "voucher_type", "voucher_no", "debit", "credit"],
        order_by="posting_date asc, creation asc"
    )


def get_chart_data(data):
    """Generate chart data"""
    # Remove opening/closing balance rows
    chart_data = [d for d in data if d.get("voucher_no") not in [_("Opening Balance"), _("Closing Balance")]]
    
    # Group by month
    monthly_data = {}
    for row in chart_data:
        month = str(row.get("posting_date", ""))[:7]
        if month not in monthly_data:
            monthly_data[month] = {"debit": 0, "credit": 0}
        monthly_data[month]["debit"] += row.get("debit", 0)
        monthly_data[month]["credit"] += row.get("credit", 0)
    
    return {
        "data": {
            "labels": list(monthly_data.keys()),
            "datasets": [
                {
                    "name": "Debit",
                    "values": [monthly_data[k]["debit"] for k in monthly_data.keys()]
                },
                {
                    "name": "Credit",
                    "values": [monthly_data[k]["credit"] for k in monthly_data.keys()]
                }
            ]
        },
        "type": "bar",
        "colors": ["#ff5858", "#28a745"]
    }


@frappe.whitelist()
def get_customer_statement(customer, from_date=None, to_date=None, company=None):
    """API endpoint for customer statement"""
    filters = {"customer": customer}
    if from_date:
        filters["from_date"] = from_date
    if to_date:
        filters["to_date"] = to_date
    if company:
        filters["company"] = company
    
    columns, data, _, chart = execute(filters)
    return {"columns": columns, "data": data, "chart": chart}
