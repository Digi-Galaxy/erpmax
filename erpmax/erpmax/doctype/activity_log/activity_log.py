# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import now_datetime
from frappe.model.document import Document

_IGNORED_DOCTYPES = {"Activity Log", "Error Log", "DocType", "Patch Log", "Scheduled Job Log", "User"}


class ActivityLog(Document):
    pass


def log_activity(user, action, doc_type=None, doc_name=None, details=None, remarks=None):
    """
    Log user activity.
    
    Args:
        user: User email
        action: Action performed
        doc_type: Document type (optional)
        doc_name: Document name (optional)
        details: Additional details (optional)
        remarks: Remarks (optional)
    """
    if doc_type in _IGNORED_DOCTYPES:
        return

    try:
        log = frappe.get_doc({
            "doctype": "Activity Log",
            "user": user,
            "action": action,
            "doc_type": doc_type,
            "doc_name": doc_name,
            "ip_address": frappe.local.request_ip if frappe.local.request_ip else None,
            "timestamp": now_datetime(),
            "details": details,
            "remarks": remarks
        })
        log.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to log activity: {str(e)}")


def get_user_activity(user, limit=100):
    """Get recent activity for a user"""
    return frappe.get_all(
        "Activity Log",
        filters={"user": user},
        fields=["action", "doc_type", "doc_name", "timestamp"],
        order_by="timestamp desc",
        limit=limit
    )


def get_document_activity(doc_type, doc_name, limit=50):
    """Get activity for a specific document"""
    return frappe.get_all(
        "Activity Log",
        filters={
            "doc_type": doc_type,
            "doc_name": doc_name
        },
        fields=["user", "action", "timestamp", "details"],
        order_by="timestamp desc",
        limit=limit
    )


def get_activity_summary(date=None, user=None):
    """Get activity summary for a date"""
    from frappe.utils import getdate
    
    if not date:
        date = getdate()
    
    filters = {
        "timestamp": ["between", [date, date]]
    }
    
    if user:
        filters["user"] = user
    
    activities = frappe.get_all(
        "Activity Log",
        filters=filters,
        fields=["user", "action"]
    )
    
    summary = {}
    for activity in activities:
        user = activity.user
        action = activity.action
        
        if user not in summary:
            summary[user] = {}
        
        if action not in summary[user]:
            summary[user][action] = 0
        
        summary[user][action] += 1
    
    return summary


@frappe.whitelist()
def get_activity_log_report(from_date=None, to_date=None, user=None, action=None):
    """Get activity log report"""
    filters = {}
    
    if from_date and to_date:
        filters["timestamp"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["timestamp"] = [">=", from_date]
    elif to_date:
        filters["timestamp"] = ["<=", to_date]
    
    if user:
        filters["user"] = user
    
    if action:
        filters["action"] = action
    
    return frappe.get_all(
        "Activity Log",
        filters=filters,
        fields=["user", "action", "doc_type", "doc_name", "timestamp", "ip_address"],
        order_by="timestamp desc",
        limit=1000
    )


# Hook into document events to log activity
def on_document_update(doc, method):
    """Log document update"""
    if doc.doctype in _IGNORED_DOCTYPES:
        return
    
    log_activity(
        user=frappe.session.user,
        action="Update",
        doc_type=doc.doctype,
        doc_name=doc.name,
        details=f"Updated {doc.doctype} {doc.name}"
    )


def on_document_create(doc, method):
    """Log document create"""
    if doc.doctype in _IGNORED_DOCTYPES:
        return
    
    log_activity(
        user=frappe.session.user,
        action="Create",
        doc_type=doc.doctype,
        doc_name=doc.name,
        details=f"Created {doc.doctype} {doc.name}"
    )


def on_document_delete(doc, method):
    """Log document delete"""
    if doc.doctype in _IGNORED_DOCTYPES:
        return
    
    log_activity(
        user=frappe.session.user,
        action="Delete",
        doc_type=doc.doctype,
        doc_name=doc.name,
        details=f"Deleted {doc.doctype} {doc.name}"
    )
