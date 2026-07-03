import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_partner_statement(company, partner_account, from_date=None, to_date=None):
    filters = {
        "company": company,
        "party_type": "Partner Account",
        "party": partner_account,
        "is_cancelled": 0,
    }
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [from_date, to_date]]
        else:
            filters["posting_date"] = ["<=", to_date]

    entries = frappe.get_all(
        "GL Entry",
        filters=filters,
        fields=["posting_date", "voucher_type", "voucher_no", "account", "debit", "credit"],
        order_by="posting_date asc, creation asc",
    )
    opening = 0
    if from_date:
        opening_rows = frappe.get_all(
            "GL Entry",
            filters={
                "company": company,
                "party_type": "Partner Account",
                "party": partner_account,
                "is_cancelled": 0,
                "posting_date": ["<", from_date],
            },
            fields=["debit", "credit"],
        )
        opening = sum(flt(r.debit) - flt(r.credit) for r in opening_rows)

    running = opening
    for row in entries:
        running += flt(row.debit) - flt(row.credit)
        row["running_balance"] = running

    return {
        "opening_balance": opening,
        "closing_balance": running,
        "entries": entries,
    }


@frappe.whitelist()
def get_partner_reconciliation_summary(company, partner_account):
    summary = get_partner_statement(company, partner_account)
    return {
        "partner_account": partner_account,
        "opening_balance": summary["opening_balance"],
        "closing_balance": summary["closing_balance"],
        "total_entries": len(summary["entries"]),
    }
