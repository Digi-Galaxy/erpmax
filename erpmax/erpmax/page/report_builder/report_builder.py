# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def get_context(context):
    """Get context for report builder page"""
    context.no_cache = 1
    context.title = _("Report Builder")
    
    # Get available doctypes
    context.doctypes = get_available_doctypes()
    
    # Get saved reports
    context.saved_reports = get_saved_reports()
    
    return context


def get_available_doctypes():
    """Get list of doctypes available for reporting"""
    doctypes = frappe.get_all(
        "DocType",
        filters={
            "istable": 0,
            "issingle": 0,
            "module": ["in", ["ERPMax", "Accounting", "Sales", "Purchase", 
                             "Inventory", "Commerce", "Banking", "Expense Management"]]
        },
        fields=["name", "module"],
        order_by="name asc"
    )
    
    return doctypes


def get_saved_reports():
    """Get list of saved custom reports"""
    return frappe.get_all(
        "Custom Report",
        fields=["name", "report_name", "doc_type", "owner", "modified"],
        order_by="modified desc",
        limit=20
    )


@frappe.whitelist()
def get_doctype_fields(doctype):
    """Get fields for a doctype"""
    meta = frappe.get_meta(doctype)
    
    fields = []
    for field in meta.fields:
        fields.append({
            "fieldname": field.fieldname,
            "fieldtype": field.fieldtype,
            "label": field.label,
            "options": field.options
        })
    
    return fields


@frappe.whitelist()
def execute_custom_report(config):
    """Execute a custom report"""
    import json
    
    if isinstance(config, str):
        config = json.loads(config)
    
    doctype = config.get("doctype")
    filters = config.get("filters", {})
    columns = config.get("columns", [])
    sorts = config.get("sorts", [])
    groups = config.get("groups", [])
    
    # Build query
    fields = [col.get("fieldname") for col in columns]
    
    # Execute query
    data = frappe.get_all(
        doctype,
        filters=filters,
        fields=fields,
        order_by=sorts,
        limit=1000
    )
    
    return {
        "columns": columns,
        "data": data,
        "total": len(data)
    }


@frappe.whitelist()
def save_report(config, report_name):
    """Save a custom report"""
    import json
    
    if isinstance(config, str):
        config = json.loads(config)
    
    # Create or update Custom Report
    report = frappe.get_doc({
        "doctype": "Custom Report",
        "report_name": report_name,
        "doc_type": config.get("doctype"),
        "config": json.dumps(config),
        "owner": frappe.session.user
    })
    
    report.insert()
    frappe.db.commit()
    
    return report.name


@frappe.whitelist()
def delete_report(report_name):
    """Delete a custom report"""
    frappe.delete_doc("Custom Report", report_name)
    frappe.db.commit()
    return True


@frappe.whitelist()
def generate_report(report_type):
    """Generate report by type"""
    try:
        if report_type == "trial_balance":
            from erpmax.accounting.report.trial_balance.trial_balance import execute
            columns, data = execute()
            return {"report_type": "Trial Balance", "data": data, "columns": columns}
        elif report_type == "general_ledger":
            from erpmax.accounting.report.general_ledger.general_ledger import execute
            columns, data = execute()
            return {"report_type": "General Ledger", "data": data, "columns": columns}
        elif report_type == "balance_sheet":
            from erpmax.accounting.report.balance_sheet.balance_sheet import execute
            columns, data = execute()
            return {"report_type": "Balance Sheet", "data": data, "columns": columns}
        elif report_type == "profit_and_loss":
            from erpmax.accounting.report.profit_and_loss.profit_and_loss import execute
            columns, data = execute()
            return {"report_type": "Profit and Loss", "data": data, "columns": columns}
        elif report_type == "sales_register":
            from erpmax.sales.report.sales_register.sales_register import execute
            columns, data = execute()
            return {"report_type": "Sales Register", "data": data, "columns": columns}
        elif report_type == "purchase_register":
            from erpmax.purchase.report.purchase_register.purchase_register import execute
            columns, data = execute()
            return {"report_type": "Purchase Register", "data": data, "columns": columns}
        elif report_type == "customer_summary":
            from erpmax.accounting.report.customer_summary.customer_summary import execute
            columns, data = execute()
            return {"report_type": "Customer Summary", "data": data, "columns": columns}
        elif report_type == "supplier_summary":
            from erpmax.accounting.report.supplier_summary.supplier_summary import execute
            columns, data = execute()
            return {"report_type": "Supplier Summary", "data": data, "columns": columns}
        else:
            return {"error": "Unknown report type: " + report_type}
    except Exception as e:
        return {"error": str(e)}
