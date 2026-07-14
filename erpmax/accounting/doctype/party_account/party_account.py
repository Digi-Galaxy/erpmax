# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class PartyAccount(Document):
    def validate(self):
        self.validate_account()
        self.validate_company()
    
    def validate_account(self):
        """Validate account exists and belongs to company"""
        if self.account:
            account = frappe.get_doc("Account", self.account)
            if account.company and account.company != self.company:
                frappe.throw(_("Account {0} does not belong to company {1}").format(
                    self.account, self.company
                ))
    
    def validate_company(self):
        """Validate company exists"""
        if self.company:
            if not frappe.db.exists("Company", self.company):
                frappe.throw(_("Company {0} does not exist").format(self.company))


def get_party_account(party_type, party_name, company):
    """
    Get account for a party, checking Party Account table first,
    then falling back to auto-created account.
    """
    # Check Party Account table first
    party_account = frappe.db.get_value(
        "Party Account",
        {
            "parenttype": party_type,
            "parent": party_name,
            "company": company,
            "is_default": 1
        },
        "account"
    )
    
    if party_account:
        return party_account
    
    # Fallback to auto-created account
    if party_type == "Customer":
        account_name = f"CUST-{party_name}"
    elif party_type == "Supplier":
        account_name = f"SUPP-{party_name}"
    else:
        account_name = f"CUST-{party_name}"
    
    account = frappe.db.get_value(
        "Account",
        {
            "account_name": account_name,
            "company": company
        },
        "name"
    )
    
    return account


def create_party_account_if_not_exists(party_type, party_name, company):
    """
    Create account for party if it doesn't exist.
    Returns the account name.
    """
    # Check if account already exists in Party Account table
    existing = frappe.db.get_value(
        "Party Account",
        {
            "parenttype": party_type,
            "parent": party_name,
            "company": company
        },
        "account"
    )
    
    if existing:
        return existing
    
    # Determine account type and prefix
    if party_type in ["Customer", "Contractor", "Distributor", "Partner", "Shareholder", "Donor"]:
        account_type = "Receivable"
        prefix = "CUST-"
    else:
        account_type = "Payable"
        prefix = "SUPP-"
    
    # Create account name
    account_name = f"{prefix}{party_name}"
    
    # Check if account already exists
    existing_account = frappe.db.get_value("Account", {
        "account_name": account_name,
        "company": company
    })
    
    if existing_account:
        # Add to Party Account table
        add_party_account(party_type, party_name, company, existing_account)
        return existing_account
    
    # Get parent account
    parent_account = frappe.db.get_value("Account", {
        "account_type": account_type,
        "is_group": 1,
        "company": company
    }, "name")
    
    if not parent_account:
        # Try without company filter
        parent_account = frappe.db.get_value("Account", {
            "account_type": account_type,
            "is_group": 1
        }, "name")
    
    if not parent_account:
        frappe.msgprint(_("No {0} group account found. Please create one first.").format(account_type))
        return None
    
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
        
        # Add to Party Account table
        add_party_account(party_type, party_name, company, account.name)
        
        frappe.msgprint(_("Account {0} created automatically").format(account_name))
        return account.name
    except Exception as e:
        frappe.log_error(f"Failed to create account for {party_name}: {str(e)}")
        return None


def add_party_account(party_type, party_name, company, account_name):
    """Add account to Party Account table"""
    # Check if already exists
    existing = frappe.db.get_value(
        "Party Account",
        {
            "parenttype": party_type,
            "parent": party_name,
            "company": company
        },
        "name"
    )
    
    if existing:
        return
    
    # Create new Party Account entry
    try:
        party_account = frappe.get_doc({
            "doctype": "Party Account",
            "parenttype": party_type,
            "parent": party_name,
            "company": company,
            "account": account_name,
            "is_default": 1
        })
        party_account.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to add party account: {str(e)}")


def get_all_party_accounts(party_type, party_name):
    """Get all accounts for a party"""
    accounts = frappe.get_all(
        "Party Account",
        filters={
            "parenttype": party_type,
            "parent": party_name
        },
        fields=["company", "account", "advance_account", "is_default"],
        order_by="is_default desc"
    )
    
    return accounts
