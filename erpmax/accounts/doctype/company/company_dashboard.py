from frappe import _


def get_data():
    return {
        "fieldname": "company",
        "transactions": [
            {"label": _("Sales"), "items": ["Sales Invoice", "Proforma Invoice"]},
            {"label": _("Purchasing"), "items": ["Purchase Invoice"]},
            {"label": _("Projects"), "items": ["Project", "Expense Claim"]},
            {"label": _("Finance"), "items": ["Journal Entry", "Payment Entry"]},
            {"label": _("Masters"), "items": ["Customer", "Supplier", "Item"]},
        ],
    }