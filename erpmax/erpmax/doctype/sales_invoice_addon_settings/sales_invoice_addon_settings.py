# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class SalesInvoiceAddonSettings(Document):
    def validate(self):
        self.validate_discount_settings()
        self.validate_payment_settings()
    
    def validate_discount_settings(self):
        if self.enable_line_discount and self.enable_invoice_discount:
            if self.max_discount_percent and self.max_discount_percent > 100:
                frappe.throw(_("Maximum discount cannot exceed 100%"))
    
    def validate_payment_settings(self):
        if self.allow_partial_payment:
            if self.min_payment_percent and (self.min_payment_percent <= 0 or self.min_payment_percent > 100):
                frappe.throw(_("Minimum payment percentage must be between 0 and 100"))


def get_addon_settings():
    """Get sales invoice addon settings"""
    try:
        return frappe.get_single("Sales Invoice Addon Settings")
    except:
        return None


def is_addon_enabled(addon_name):
    """Check if a specific addon is enabled"""
    settings = get_addon_settings()
    if not settings:
        return False
    
    addon_field = f"enable_{addon_name}"
    return getattr(settings, addon_field, False)


def get_outstanding_balance(customer, company=None):
    """Get outstanding balance for a customer"""
    filters = {
        "customer": customer,
        "outstanding_amount": [">", 0],
        "docstatus": 1
    }
    
    if company:
        filters["company"] = company
    
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "grand_total", "outstanding_amount", "due_date"]
    )
    
    total_outstanding = sum(inv.outstanding_amount for inv in invoices)
    overdue_count = sum(1 for inv in invoices if inv.due_date and inv.due_date < getdate())
    
    return {
        "total_outstanding": total_outstanding,
        "invoice_count": len(invoices),
        "overdue_count": overdue_count,
        "invoices": invoices
    }


def get_payment_suggestions(outstanding_amount):
    """Get payment suggestions based on outstanding amount"""
    suggestions = []
    
    # Full payment
    suggestions.append({
        "label": "Full Payment",
        "amount": outstanding_amount,
        "description": "Pay the full outstanding amount"
    })
    
    # Partial payments
    percentages = [25, 50, 75]
    for pct in percentages:
        amount = outstanding_amount * (pct / 100)
        suggestions.append({
            "label": f"{pct}% Payment",
            "amount": amount,
            "description": f"Pay {pct}% of outstanding amount"
        })
    
    # Custom amount
    suggestions.append({
        "label": "Custom Amount",
        "amount": None,
        "description": "Enter a custom payment amount"
    })
    
    return suggestions
