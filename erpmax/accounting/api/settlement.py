import frappe

@frappe.whitelist()
def get_party_account(party_type, party, company):
    """Get default receivable/payable account for a party."""
    if party_type == "Customer":
        account = frappe.db.get_value("Customer", party, "default_receivable_account")
        if not account:
            account = frappe.db.get_value("Company", company, "default_receivable_account")
        return account
    elif party_type == "Supplier":
        account = frappe.db.get_value("Supplier", party, "default_payable_account")
        if not account:
            account = frappe.db.get_value("Company", company, "default_payable_account")
        return account
    return None
