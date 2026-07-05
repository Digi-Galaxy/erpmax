# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class CompanyUser(Document):
    def validate(self):
        self.validate_user()
        self.validate_company()
        self.validate_permissions()
    
    def validate_user(self):
        """Validate user email"""
        if not self.user_email:
            frappe.throw(_("User Email is required"))
    
    def validate_company(self):
        """Validate company exists"""
        if not frappe.db.exists("Company", self.company):
            frappe.throw(_("Company {0} does not exist").format(self.company))
    
    def validate_permissions(self):
        """Validate permission settings"""
        if not self.can_read:
            frappe.throw(_("User must have at least Read permission"))
    
    def after_insert(self):
        """Create or update user after insert"""
        self.create_or_update_user()
    
    def create_or_update_user(self):
        """Create or update Frappe user"""
        # Check if user already exists
        existing_user = frappe.db.get_value("User", {"email": self.user_email})
        
        if existing_user:
            # Update existing user
            self.update_user(existing_user)
        else:
            # Create new user
            self.create_user()
    
    def create_user(self):
        """Create new Frappe user"""
        try:
            user = frappe.get_doc({
                "doctype": "User",
                "email": self.user_email,
                "first_name": self.user_name,
                "user_type": "System User",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            
            # Add role
            self.add_role(user.name)
            
            # Set company permissions
            self.set_company_permissions(user.name)
            
            frappe.db.commit()
            frappe.msgprint(_("User {0} created successfully").format(self.user_email))
            
        except Exception as e:
            frappe.log_error(f"Failed to create user {self.user_email}: {str(e)}")
            frappe.throw(_("Failed to create user: {0}").format(str(e)))
    
    def update_user(self, user_name):
        """Update existing user"""
        try:
            user = frappe.get_doc("User", user_name)
            
            # Update first name
            user.first_name = self.user_name
            
            # Add role if not already added
            self.add_role(user_name)
            
            # Set company permissions
            self.set_company_permissions(user_name)
            
            user.save(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(f"Failed to update user {user_name}: {str(e)}")
    
    def add_role(self, user_name):
        """Add role to user"""
        role_map = {
            "Company Admin": "Company Admin",
            "Accounts Manager": "Accounts Manager",
            "Accounts User": "Accounts User",
            "Sales Manager": "Sales Manager",
            "Sales User": "Sales User",
            "Purchase Manager": "Purchase Manager",
            "Purchase User": "Purchase User",
            "Inventory Manager": "Inventory Manager",
            "Inventory User": "Inventory User"
        }
        
        role_name = role_map.get(self.role, self.role)
        
        # Check if role already exists
        existing = frappe.db.get_value(
            "Has Role",
            {"parent": user_name, "role": role_name}
        )
        
        if not existing:
            user = frappe.get_doc("User", user_name)
            user.append("roles", {"role": role_name})
            user.save(ignore_permissions=True)
    
    def set_company_permissions(self, user_name):
        """Set company-level permissions for user"""
        # Create user permission for company
        existing = frappe.db.get_value(
            "User Permission",
            {
                "user": user_name,
                "allow": "Company",
                "value": self.company
            }
        )
        
        if not existing:
            user_perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": user_name,
                "allow": "Company",
                "value": self.company,
                "is_default": 1
            })
            user_perm.insert(ignore_permissions=True)
        
        # Set default company for user
        frappe.db.set_value("User", user_name, "default_company", self.company)
        
        frappe.db.commit()
    
    def deactivate_user(self):
        """Deactivate user"""
        if self.user_email:
            try:
                user = frappe.get_doc("User", self.user_email)
                user.enabled = 0
                user.save(ignore_permissions=True)
                frappe.db.commit()
                self.is_active = 0
                self.db_update()
                frappe.msgprint(_("User {0} deactivated").format(self.user_email))
            except Exception as e:
                frappe.log_error(f"Failed to deactivate user: {str(e)}")
    
    def activate_user(self):
        """Activate user"""
        if self.user_email:
            try:
                user = frappe.get_doc("User", self.user_email)
                user.enabled = 1
                user.save(ignore_permissions=True)
                frappe.db.commit()
                self.is_active = 1
                self.db_update()
                frappe.msgprint(_("User {0} activated").format(self.user_email))
            except Exception as e:
                frappe.log_error(f"Failed to activate user: {str(e)}")


def create_company_user(company, email, name, role):
    """Helper function to create a company user"""
    try:
        user = frappe.get_doc({
            "doctype": "Company User",
            "company": company,
            "user_email": email,
            "user_name": name,
            "role": role,
            "is_active": 1
        })
        user.insert(ignore_permissions=True)
        frappe.db.commit()
        return user.name
    except Exception as e:
        frappe.log_error(f"Failed to create company user: {str(e)}")
        return None


def get_company_users(company):
    """Get all users for a company"""
    users = frappe.get_all(
        "Company User",
        filters={
            "company": company,
            "is_active": 1
        },
        fields=["user_email", "user_name", "role", "is_active"],
        order_by="user_name"
    )
    
    return users
