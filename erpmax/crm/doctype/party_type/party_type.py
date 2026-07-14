# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class PartyType(Document):
    def validate(self):
        self.validate_account_settings()
    
    def validate_account_settings(self):
        if self.auto_create_account:
            if not self.default_receivable_account and not self.default_payable_account:
                frappe.throw(_("At least one default account is required when Auto Create Account is enabled"))


def create_party_account(party_type, party_name, company=None):
    """
    Auto-create account for a party when created.
    This function is called from Customer, Supplier, or other party doctypes.
    """
    # Get party type settings
    party_type_doc = frappe.get_doc("Party Type", party_type)
    
    if not party_type_doc.auto_create_account:
        return None
    
    # Get company
    if not company:
        company = frappe.defaults.get_default("company")
    
    if not company:
        frappe.throw(_("Company is required"))
    
    # Determine account type based on party type
    account_type = "Receivable" if party_type in ["Customer", "Contractor", "Distributor", "Partner", "Shareholder", "Donor"] else "Payable"
    
    # Get account name
    account_name = f"{party_type_doc.account_prefix or ''}{party_name}"
    
    # Get parent account
    if account_type == "Receivable":
        parent_account = party_type_doc.default_receivable_account or "Accounts Receivable - ERPMax"
    else:
        parent_account = party_type_doc.default_payable_account or "Accounts Payable - ERPMax"
    
    # Check if account already exists
    existing_account = frappe.db.get_value("Account", {
        "account_name": account_name,
        "company": company
    })
    
    if existing_account:
        return existing_account
    
    # Create account
    try:
        account = frappe.get_doc({
            "doctype": "Account",
            "account_name": account_name,
            "account_type": account_type,
            "root_type": "Asset" if account_type == "Receivable" else "Liability",
            "company": company,
            "parent_account": parent_account,
            "is_group": 0
        })
        account.insert(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.msgprint(_("Account {0} created successfully").format(account_name))
        return account.name
    except Exception as e:
        frappe.log_error(f"Failed to create account for {party_name}: {str(e)}")
        return None


def get_party_accounts(party_type, party_name, company=None):
    """Get all accounts for a party"""
    if not company:
        company = frappe.defaults.get_default("company")
    
    accounts = frappe.get_all(
        "Account",
        filters={
            "account_name": ["like", f"%{party_name}%"],
            "company": company
        },
        fields=["name", "account_name", "account_type"]
    )
    
    return accounts
