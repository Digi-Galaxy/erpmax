from frappe import _


def get_data():
    return {
        "fieldname": "company",
        "transactions": [
            {"label": _("Sales"), "items": ["Sales Invoice", "Sales Order", "Delivery Note"]},
            {"label": _("Purchasing"), "items": ["Purchase Invoice", "Purchase Order", "Purchase Receipt"]},
            {"label": _("Projects"), "items": ["Project", "Expense Claim"]},
        ],
    }
