from frappe import _


def get_data():
    return {
        "fieldname": "account",
        "transactions": [
            {"label": _("Journal Entries"), "items": ["Journal Entry"]},
        ],
    }
