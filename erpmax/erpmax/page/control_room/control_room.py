# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days, cint


def get_context(context):
    """Get context for control room page"""
    context.no_cache = 1
    context.title = _("Control Room")
    
    # Get real-time data
    context.dashboard_data = get_dashboard_data()
    context.chart_data = get_chart_data()
    context.recent_activities = get_recent_activities()
    context.system_status = get_system_status()
    
    return context


def get_dashboard_data():
    """Get dashboard data for control room"""
    today = getdate()
    this_month_start = today.replace(day=1)
    
    # Sales data
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "posting_date": ["between", [this_month_start, today]]},
        fields=["grand_total"]
    )
    total_sales = sum(si.grand_total for si in sales_invoices)
    
    # Purchase data
    purchase_invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"docstatus": 1, "posting_date": ["between", [this_month_start, today]]},
        fields=["grand_total"]
    )
    total_purchases = sum(pi.grand_total for pi in purchase_invoices)
    
    # Payments data
    payment_entries = frappe.get_all(
        "Payment Entry",
        filters={"docstatus": 1, "posting_date": ["between", [this_month_start, today]]},
        fields=["paid_amount"]
    )
    total_payments = sum(pe.paid_amount for pe in payment_entries)
    
    # Outstanding data
    outstanding_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"outstanding_amount": [">", 0], "docstatus": 1},
        fields=["outstanding_amount"]
    )
    total_outstanding = sum(si.outstanding_amount for si in outstanding_invoices)
    
    # Customer count
    customer_count = frappe.db.count("Customer")
    
    # Supplier count
    supplier_count = frappe.db.count("Supplier")
    
    # Item count
    item_count = frappe.db.count("Item")
    
    return {
        "total_sales": flt(total_sales, 2),
        "total_purchases": flt(total_purchases, 2),
        "total_payments": flt(total_payments, 2),
        "total_outstanding": flt(total_outstanding, 2),
        "customer_count": customer_count,
        "supplier_count": supplier_count,
        "item_count": item_count,
        "net_profit": flt(total_sales - total_purchases, 2)
    }


def get_chart_data():
    """Get chart data for control room"""
    today = getdate()
    
    # Last 7 days sales
    sales_data = []
    for i in range(6, -1, -1):
        date = add_days(today, -i)
        sales = frappe.get_all(
            "Sales Invoice",
            filters={"docstatus": 1, "posting_date": date},
            fields=["grand_total"]
        )
        total = sum(si.grand_total for si in sales)
        sales_data.append({"date": str(date), "value": flt(total, 2)})
    
    # Last 7 days purchases
    purchase_data = []
    for i in range(6, -1, -1):
        date = add_days(today, -i)
        purchases = frappe.get_all(
            "Purchase Invoice",
            filters={"docstatus": 1, "posting_date": date},
            fields=["grand_total"]
        )
        total = sum(pi.grand_total for pi in purchases)
        purchase_data.append({"date": str(date), "value": flt(total, 2)})
    
    # Top customers by sales
    top_customers = frappe.db.sql("""
        SELECT customer_name, SUM(grand_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND posting_date >= %s
        GROUP BY customer_name
        ORDER BY total DESC
        LIMIT 5
    """, (add_days(today, -30),), as_dict=True)
    
    # Top suppliers by purchases
    top_suppliers = frappe.db.sql("""
        SELECT supplier_name, SUM(grand_total) as total
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND posting_date >= %s
        GROUP BY supplier_name
        ORDER BY total DESC
        LIMIT 5
    """, (add_days(today, -30),), as_dict=True)
    
    # Expense breakdown
    expense_breakdown = frappe.db.sql("""
        SELECT gl.account, SUM(gl.debit) as amount
        FROM `tabGL Entry` gl
        LEFT JOIN `tabAccount` acc ON acc.name = gl.account
        WHERE acc.is_group = 0 AND gl.posting_date >= %s
        GROUP BY gl.account
        ORDER BY amount DESC
        LIMIT 5
    """, (add_days(today, -30),), as_dict=True)
    
    return {
        "sales_trend": sales_data,
        "purchase_trend": purchase_data,
        "top_customers": top_customers,
        "top_suppliers": top_suppliers,
        "expense_breakdown": expense_breakdown
    }


def get_recent_activities():
    """Get recent activities"""
    return frappe.get_all(
        "Activity Log",
        fields=["user", "action", "doc_type", "doc_name", "timestamp"],
        order_by="timestamp desc",
        limit=10
    )


def get_system_status():
    """Get system status"""
    # Count documents
    doc_counts = {
        "Sales Invoice": frappe.db.count("Sales Invoice", {"docstatus": 1}),
        "Purchase Invoice": frappe.db.count("Purchase Invoice", {"docstatus": 1}),
        "Journal Entry": frappe.db.count("Journal Entry", {"docstatus": 1}),
        "Payment Entry": frappe.db.count("Payment Entry", {"docstatus": 1}),
        "Customer": frappe.db.count("Customer"),
        "Supplier": frappe.db.count("Supplier"),
        "Item": frappe.db.count("Item"),
        "Account": frappe.db.count("Account"),
    }
    
    # Get enabled modules
    from erpmax.utils.modules import get_enabled_modules
    enabled_modules = get_enabled_modules()
    
    return {
        "document_counts": doc_counts,
        "enabled_modules": enabled_modules,
        "version": "1.0.0",
        "last_backup": "Not available"
    }


@frappe.whitelist()
def get_realtime_data():
    """API endpoint for real-time dashboard updates"""
    return {
        "dashboard": get_dashboard_data(),
        "charts": get_chart_data(),
        "status": get_system_status()
    }


@frappe.whitelist()
def refresh_dashboard():
    """Refresh dashboard data"""
    return get_dashboard_data()
