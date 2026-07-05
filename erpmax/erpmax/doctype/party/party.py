# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class Party(Document):
    def validate(self):
        self.validate_party_type()
        self.set_default_accounts()
    
    def after_insert(self):
        """Auto-create account when party is created"""
        if self.auto_create_account:
            self.create_party_account()
    
    def validate_party_type(self):
        """Validate party type settings"""
        valid_types = ["Customer", "Supplier", "Contractor", "Distributor", 
                      "Partner", "Shareholder", "Donor"]
        if self.party_type not in valid_types:
            frappe.throw(_("Invalid party type: {0}").format(self.party_type))
    
    def set_default_accounts(self):
        """Set default accounts based on party type"""
        if self.party_type in ["Customer", "Contractor", "Distributor", "Partner", "Shareholder", "Donor"]:
            if not self.receivable_account:
                self.receivable_account = self._get_default_account("Receivable")
            if not self.default_income_account:
                self.default_income_account = self._get_default_account("Income")
        elif self.party_type == "Supplier":
            if not self.payable_account:
                self.payable_account = self._get_default_account("Payable")
            if not self.default_expense_account:
                self.default_expense_account = self._get_default_account("Expense")
    
    def create_party_account(self):
        """Auto-create account for party"""
        # Get company
        company = self.company or frappe.defaults.get_default("company")
        if not company:
            return
        
        # Determine account type and prefix
        if self.party_type in ["Customer", "Contractor", "Distributor", "Partner", "Shareholder", "Donor"]:
            account_type = "Receivable"
            prefix = "CUST-"
        else:
            account_type = "Payable"
            prefix = "SUPP-"
        
        # Create account name
        account_name = f"{prefix}{self.party_name}"
        
        # Check if account already exists
        existing = frappe.db.get_value("Account", {
            "account_name": account_name,
            "company": company
        })
        
        if existing:
            if account_type == "Receivable":
                self.receivable_account = existing
            else:
                self.payable_account = existing
            return
        
        # Get parent account
        parent_account = self._get_default_account(account_type)
        if not parent_account:
            frappe.msgprint(_("No {0} account found. Please create one first.").format(account_type))
            return
        
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
            
            if account_type == "Receivable":
                self.receivable_account = account.name
            else:
                self.payable_account = account.name
            
            frappe.msgprint(_("Account {0} created automatically").format(account_name))
        except Exception as e:
            frappe.log_error(f"Failed to create account for party {self.party_name}: {str(e)}")
    
    def _get_default_account(self, account_type):
        """Get default account for party type"""
        if self.company:
            account = frappe.db.get_value("Account", {
                "company": self.company,
                "account_type": account_type,
                "is_group": 0
            }, "name")
            if account:
                return account
        
        account = frappe.db.get_value("Account", {
            "account_type": account_type,
            "is_group": 0
        }, "name")
        return account
