# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class Budget(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_budget_details()
        self.validate_duplicates()
    
    def calculate_totals(self):
        """Calculate total allocated and actual amounts"""
        self.total_allocated = 0
        self.total_actual = 0
        
        for detail in self.budget_details:
            self.total_allocated += flt(detail.allocated_amount)
            self.total_actual += flt(detail.actual_amount)
            
            # Calculate utilized percentage
            if detail.allocated_amount > 0:
                detail.utilized_percent = (detail.actual_amount / detail.allocated_amount) * 100
            else:
                detail.utilized_percent = 0
        
        self.variance = self.total_allocated - self.total_actual
    
    def validate_budget_details(self):
        """Validate budget details"""
        if not self.budget_details:
            frappe.throw(_("At least one budget detail is required"))
        
        for detail in self.budget_details:
            if flt(detail.allocated_amount) <= 0:
                frappe.throw(_("Row {0}: Allocated amount must be greater than 0").format(detail.idx))
    
    def validate_duplicates(self):
        """Check for duplicate accounts in budget details"""
        accounts = []
        for detail in self.budget_details:
            if detail.account in accounts:
                frappe.throw(_("Row {0}: Account {1} is already added").format(detail.idx, detail.account))
            accounts.append(detail.account)
    
    def on_submit(self):
        """Actions on submit"""
        self.status = "Submitted"
        self.update_actual_amounts()
        self.db_update()
    
    def on_cancel(self):
        """Actions on cancel"""
        self.status = "Cancelled"
        self.db_update()
    
    def approve(self):
        """Approve the budget"""
        if self.docstatus != 1:
            frappe.throw(_("Budget must be submitted before approval"))
        
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = getdate(nowdate())
        self.db_update()
        
        frappe.msgprint(_("Budget {0} approved successfully").format(self.name))
    
    def reject(self):
        """Reject the budget"""
        if self.docstatus != 1:
            frappe.throw(_("Budget must be submitted before rejection"))
        
        self.status = "Rejected"
        self.db_update()
        
        frappe.msgprint(_("Budget {0} rejected").format(self.name))
    
    def update_actual_amounts(self):
        """Update actual amounts from GL entries"""
        for detail in self.budget_details:
            actual = get_account_actual_amount(
                detail.account, 
                self.fiscal_year, 
                self.company
            )
            detail.actual_amount = flt(actual)
    
    def get_budget_status(self):
        """Get budget utilization status"""
        if self.total_allocated == 0:
            return "No Budget"
        
        utilized_percent = (self.total_actual / self.total_allocated) * 100
        
        if utilized_percent >= 100:
            return "Exceeded"
        elif utilized_percent >= 90:
            return "Warning"
        elif utilized_percent >= 75:
            return "On Track"
        else:
            return "Under Budget"


def get_account_actual_amount(account, fiscal_year, company):
    """Get actual amount for an account in a fiscal year"""
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    
    gl_entries = frappe.get_all(
        "GL Entry",
        filters={
            "account": account,
            "company": company,
            "posting_date": ["between", [fiscal_year_doc.year_start_date, fiscal_year_doc.year_end_date]],
            "is_cancelled": 0,
        },
        fields=["debit", "credit"]
    )
    
    total_debit = sum(flt(entry.debit) for entry in gl_entries)
    total_credit = sum(flt(entry.credit) for entry in gl_entries)
    
    # For expense accounts, return debit - credit
    # For income accounts, return credit - debit
    account_root_type = frappe.db.get_value("Account", account, "root_type")
    
    if account_root_type == "Expense":
        return total_debit - total_credit
    else:
        return total_credit - total_debit


@frappe.whitelist()
def get_budget_summary(company, fiscal_year):
    """Get budget summary for dashboard"""
    budgets = frappe.get_all(
        "Budget",
        filters={
            "company": company,
            "fiscal_year": fiscal_year,
            "docstatus": 1,
            "status": ["in", ["Submitted", "Approved"]]
        },
        fields=["name", "budget_name", "total_allocated", "total_actual", "variance"]
    )
    
    total_allocated = sum(b.total_allocated for b in budgets)
    total_actual = sum(b.total_actual for b in budgets)
    
    return {
        "budgets": budgets,
        "total_allocated": total_allocated,
        "total_actual": total_actual,
        "total_variance": total_allocated - total_actual,
        "utilized_percent": (total_actual / total_allocated * 100) if total_allocated > 0 else 0
    }


@frappe.whitelist()
def check_budget_availability(account, amount, company, fiscal_year):
    """Check if budget is available for an account"""
    budget = frappe.db.get_value(
        "Budget",
        {
            "company": company,
            "fiscal_year": fiscal_year,
            "docstatus": 1,
            "status": "Approved"
        },
        "name"
    )
    
    if not budget:
        return {"available": True, "message": "No budget configured"}
    
    budget_doc = frappe.get_doc("Budget", budget)
    
    for detail in budget_doc.budget_details:
        if detail.account == account:
            remaining = detail.allocated_amount - detail.actual_amount
            
            if amount > remaining:
                return {
                    "available": False,
                    "message": _("Budget exceeded. Available: {0}, Requested: {1}").format(remaining, amount),
                    "allocated": detail.allocated_amount,
                    "actual": detail.actual_amount,
                    "remaining": remaining
                }
            
            return {
                "available": True,
                "message": _("Budget available. Remaining: {0}").format(remaining),
                "allocated": detail.allocated_amount,
                "actual": detail.actual_amount,
                "remaining": remaining
            }
    
    return {"available": True, "message": "Account not in budget"}
