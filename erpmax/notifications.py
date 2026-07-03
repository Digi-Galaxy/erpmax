import frappe


def get_notification_config():
    """Return notification configuration for ERPMax"""
    return {
        "for_doctype": {
            "Sales Invoice": {"status": "Overdue"},
            "Purchase Invoice": {"status": "Overdue"},
            "Payment Entry": {"docstatus": 0},
            "Journal Entry": {"docstatus": 0},
        },
        "for_module": {
            "Accounts": ["GL Entry", "Payment Entry"],
            "Sales": ["Sales Invoice"],
            "Purchase": ["Purchase Invoice"],
        }
    }
