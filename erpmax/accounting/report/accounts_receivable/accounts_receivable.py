# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_days


def execute(filters=None):
    """Accounts Receivable Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "customer",
            "fieldtype": "Link",
            "label": _("Customer"),
            "options": "Customer",
            "width": 200,
        },
        {
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "label": _("Customer Name"),
            "width": 200,
        },
        {
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "label": _("Invoice No"),
            "options": "Sales Invoice",
            "width": 150,
        },
        {
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "label": _("Invoice Date"),
            "width": 100,
        },
        {
            "fieldname": "due_date",
            "fieldtype": "Date",
            "label": _("Due Date"),
            "width": 100,
        },
        {
            "fieldname": "amount",
            "fieldtype": "Currency",
            "label": _("Amount"),
            "width": 120,
        },
        {
            "fieldname": "outstanding",
            "fieldtype": "Currency",
            "label": _("Outstanding"),
            "width": 120,
        },
        {
            "fieldname": "aging_bucket",
            "fieldtype": "Data",
            "label": _("Aging Bucket"),
            "width": 120,
        },
    ]


def get_data(filters):
    """Get accounts receivable data"""
    report_date = filters.get("report_date") or frappe.utils.nowdate()
    customer = filters.get("customer")
    company = filters.get("company")
    
    # Build filters
    si_filters = {
        "outstanding_amount": [">", 0],
        "docstatus": 1,
    }
    
    if customer:
        si_filters["customer"] = customer
    if company:
        si_filters["company"] = company
    
    # Get unpaid sales invoices
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=si_filters,
        fields=[
            "name", "customer", "customer_name", "posting_date",
            "due_date", "grand_total", "outstanding_amount"
        ],
        order_by="due_date asc"
    )
    
    data = []
    for invoice in invoices:
        # Calculate aging bucket
        aging_bucket = calculate_aging_bucket(
            invoice.due_date, report_date
        )
        
        data.append({
            "customer": invoice.customer,
            "customer_name": invoice.customer_name,
            "invoice_no": invoice.name,
            "posting_date": invoice.posting_date,
            "due_date": invoice.due_date,
            "amount": flt(invoice.grand_total, 2),
            "outstanding": flt(invoice.outstanding_amount, 2),
            "aging_bucket": aging_bucket,
        })
    
    # Add totals
    total_amount = sum(d.get("amount", 0) for d in data)
    total_outstanding = sum(d.get("outstanding", 0) for d in data)
    
    data.append({
        "customer": "",
        "customer_name": _("Total"),
        "invoice_no": "",
        "posting_date": None,
        "due_date": None,
        "amount": flt(total_amount, 2),
        "outstanding": flt(total_outstanding, 2),
        "aging_bucket": "",
    })
    
    return data


def calculate_aging_bucket(due_date, report_date):
    """Calculate aging bucket based on due date"""
    if not due_date:
        return "Unknown"
    
    days_overdue = (getdate(report_date) - getdate(due_date)).days
    
    if days_overdue <= 0:
        return "Current"
    elif days_overdue <= 30:
        return "1-30 Days"
    elif days_overdue <= 60:
        return "31-60 Days"
    elif days_overdue <= 90:
        return "61-90 Days"
    else:
        return "90+ Days"


def get_chart_data(data):
    """Generate chart data for accounts receivable"""
    # Remove totals row
    chart_data = [d for d in data if d.get("invoice_no")]
    
    # Group by aging bucket
    aging_totals = {}
    for row in chart_data:
        bucket = row.get("aging_bucket", "Unknown")
        if bucket not in aging_totals:
            aging_totals[bucket] = 0
        aging_totals[bucket] += row.get("outstanding", 0)
    
    # Sort by bucket order
    bucket_order = ["Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"]
    sorted_buckets = [b for b in bucket_order if b in aging_totals]
    
    return {
        "data": {
            "labels": sorted_buckets,
            "datasets": [
                {
                    "name": "Outstanding",
                    "values": [aging_totals[b] for b in sorted_buckets]
                }
            ]
        },
        "type": "bar",
        "colors": ["#ff5858"]
    }


@frappe.whitelist()
def get_accounts_receivable(report_date=None, customer=None, company=None):
    """API endpoint for accounts receivable"""
    filters = {}
    if report_date:
        filters["report_date"] = report_date
    if customer:
        filters["customer"] = customer
    if company:
        filters["company"] = company
    
    columns, data, _, chart = execute(filters)
    return {"columns": columns, "data": data, "chart": chart}
