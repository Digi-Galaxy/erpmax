# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class CompanyAccountSetup(Document):
    def validate(self):
        self.validate_company()
    
    def validate_company(self):
        """Validate company exists"""
        if not frappe.db.exists("Company", self.company):
            frappe.throw(_("Company {0} does not exist").format(self.company))
    
    def setup_accounts(self):
        """Setup all accounts for the company"""
        errors = []
        created = 0
        
        try:
            # Create Receivable accounts
            if self.create_receivable:
                count = self.create_receivable_accounts()
                created += count
            
            # Create Payable accounts
            if self.create_payable:
                count = self.create_payable_accounts()
                created += count
            
            # Create Income accounts
            if self.create_income:
                count = self.create_income_accounts()
                created += count
            
            # Create Expense accounts
            if self.create_expense:
                count = self.create_expense_accounts()
                created += count
            
            # Create Bank accounts
            if self.create_bank:
                count = self.create_bank_accounts()
                created += count
            
            # Create Cash accounts
            if self.create_cash:
                count = self.create_cash_accounts()
                created += count
            
            # Update status
            self.accounts_created = created
            self.last_run = frappe.utils.now_datetime()
            self.status = "Completed"
            self.db_update()
            
            frappe.msgprint(_("{0} accounts created successfully").format(created))
            
        except Exception as e:
            self.status = "Failed"
            self.errors = str(e)
            self.db_update()
            frappe.throw(_("Error setting up accounts: {0}").format(str(e)))
    
    def create_receivable_accounts(self):
        """Create receivable accounts"""
        accounts = [
            {"name": "Accounts Receivable", "type": "Receivable", "root": "Asset"},
            {"name": "Customer Deposits", "type": "Receivable", "root": "Asset"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_payable_accounts(self):
        """Create payable accounts"""
        accounts = [
            {"name": "Accounts Payable", "type": "Payable", "root": "Liability"},
            {"name": "Vendor Deposits", "type": "Payable", "root": "Liability"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_income_accounts(self):
        """Create income accounts"""
        accounts = [
            {"name": "Sales", "type": "Income", "root": "Income"},
            {"name": "Service Income", "type": "Income", "root": "Income"},
            {"name": "Other Income", "type": "Income", "root": "Income"},
            {"name": "Interest Income", "type": "Income", "root": "Income"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_expense_accounts(self):
        """Create expense accounts"""
        accounts = [
            {"name": "Cost of Goods Sold", "type": "Expense", "root": "Expense"},
            {"name": "Salary Expense", "type": "Expense", "root": "Expense"},
            {"name": "Rent Expense", "type": "Expense", "root": "Expense"},
            {"name": "Utilities Expense", "type": "Expense", "root": "Expense"},
            {"name": "Office Supplies", "type": "Expense", "root": "Expense"},
            {"name": "Marketing Expense", "type": "Expense", "root": "Expense"},
            {"name": "Travel Expense", "type": "Expense", "root": "Expense"},
            {"name": "Depreciation Expense", "type": "Expense", "root": "Expense"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_bank_accounts(self):
        """Create bank accounts"""
        accounts = [
            {"name": "Bank Account", "type": "Bank", "root": "Asset"},
            {"name": "Petty Cash", "type": "Cash", "root": "Asset"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_cash_accounts(self):
        """Create cash accounts"""
        accounts = [
            {"name": "Cash", "type": "Cash", "root": "Asset"},
            {"name": "Cash in Hand", "type": "Cash", "root": "Asset"},
        ]
        
        count = 0
        for account in accounts:
            if self.create_account_if_not_exists(
                account["name"], account["type"], account["root"]
            ):
                count += 1
        
        return count
    
    def create_account_if_not_exists(self, account_name, account_type, root_type):
        """Create account if it doesn't exist"""
        # Check if account already exists
        existing = frappe.db.get_value("Account", {
            "account_name": account_name,
            "company": self.company
        })
        
        if existing:
            return False
        
        # Get parent account
        parent_account = frappe.db.get_value("Account", {
            "account_type": account_type,
            "root_type": root_type,
            "is_group": 1,
            "company": self.company
        }, "name")
        
        if not parent_account:
            # Try without company filter
            parent_account = frappe.db.get_value("Account", {
                "account_type": account_type,
                "root_type": root_type,
                "is_group": 1
            }, "name")
        
        if not parent_account:
            frappe.log_error(f"No parent account found for {account_type}/{root_type}")
            return False
        
        # Create account
        try:
            account = frappe.get_doc({
                "doctype": "Account",
                "account_name": account_name,
                "account_type": account_type,
                "root_type": root_type,
                "company": self.company,
                "parent_account": parent_account,
                "is_group": 0
            })
            account.insert(ignore_permissions=True)
            frappe.db.commit()
            return True
        except Exception as e:
            frappe.log_error(f"Failed to create account {account_name}: {str(e)}")
            return False


def setup_company_accounts(company_name):
    """Setup accounts for a company (called from company setup)"""
    try:
        setup = frappe.get_doc({
            "doctype": "Company Account Setup",
            "company": company_name,
            "create_receivable": 1,
            "create_payable": 1,
            "create_income": 1,
            "create_expense": 1,
            "create_bank": 1,
            "create_cash": 1
        })
        setup.insert(ignore_permissions=True)
        setup.setup_accounts()
        frappe.db.commit()
        return setup.accounts_created
    except Exception as e:
        frappe.log_error(f"Failed to setup company accounts: {str(e)}")
        return 0
