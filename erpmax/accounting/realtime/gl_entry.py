"""GL Entry realtime hook - publish live updates to dashboard"""
import frappe


def collect_gl_entry(doc, method):
    """After GL Entry is inserted, publish realtime event for dashboard."""
    try:
        # Get account root type
        root_type = frappe.db.get_value("Account", doc.account, "root_type")
        
        frappe.publish_realtime(
            "erpmax_gl_posted",
            {
                "company": doc.company,
                "voucher_type": doc.voucher_type,
                "voucher_no": doc.voucher_no,
                "account": doc.account,
                "root_type": root_type,
                "debit": doc.debit,
                "credit": doc.credit,
                "posting_date": str(doc.posting_date) if doc.posting_date else None,
                "is_cancelled": doc.is_cancelled,
            },
            user=doc.owner,
        )
    except Exception:
        pass
