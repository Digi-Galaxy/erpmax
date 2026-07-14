# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PaymentTerm(Document):
    def validate(self):
        self.validate_percentage()
        self.validate_duplicates()
    
    def validate_percentage(self):
        """Validate that total percentage is 100%"""
        if not self.payment_terms_details:
            frappe.throw(_("At least one payment term detail is required"))
        
        total_percentage = sum(flt(detail.percentage) for detail in self.payment_terms_details)
        
        if abs(total_percentage - 100) > 0.01:
            frappe.throw(_("Total percentage must be 100%. Current total: {0}%").format(total_percentage))
    
    def validate_duplicates(self):
        """Check for duplicate descriptions"""
        descriptions = []
        for detail in self.payment_terms_details:
            if detail.description in descriptions:
                frappe.throw(_("Row {0}: Description '{1}' is already added").format(detail.idx, detail.description))
            descriptions.append(detail.description)
    
    def calculate_amounts(self, total_amount):
        """Calculate amounts based on total invoice amount"""
        for detail in self.payment_terms_details:
            detail.amount = flt(total_amount) * flt(detail.percentage) / 100


def get_payment_terms_details(payment_term_name, total_amount):
    """Get payment terms breakdown for an invoice"""
    payment_term = frappe.get_doc("Payment Term", payment_term_name)
    
    details = []
    for detail in payment_term.payment_terms_details:
        amount = flt(total_amount) * flt(detail.percentage) / 100
        details.append({
            "description": detail.description,
            "due_date_days": detail.due_date,
            "percentage": detail.percentage,
            "amount": flt(amount, 2)
        })
    
    return details


@frappe.whitelist()
def create_payment_schedule(payment_term_name, invoice_date, total_amount):
    """Create payment schedule for an invoice"""
    from frappe.utils import add_days, getdate
    
    payment_term = frappe.get_doc("Payment Term", payment_term_name)
    invoice_date = getdate(invoice_date)
    
    schedule = []
    for detail in payment_term.payment_terms_details:
        due_date = add_days(invoice_date, int(detail.due_date))
        amount = flt(total_amount) * flt(detail.percentage) / 100
        
        schedule.append({
            "description": detail.description,
            "due_date": due_date,
            "percentage": detail.percentage,
            "amount": flt(amount, 2),
            "status": "Pending"
        })
    
    return schedule
