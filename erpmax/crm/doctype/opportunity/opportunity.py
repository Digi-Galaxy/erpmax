# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class Opportunity(Document):
    def validate(self):
        self.validate_lead_or_customer()
        self.validate_amount()
    
    def validate_lead_or_customer(self):
        """Validate that either lead or customer is provided"""
        if not self.lead and not self.customer:
            frappe.throw(_("Either Lead or Customer is required"))
    
    def validate_amount(self):
        """Validate expected amount"""
        if self.expected_amount and flt(self.expected_amount) <= 0:
            frappe.throw(_("Expected Amount must be greater than 0"))
    
    def on_update(self):
        """Actions on update"""
        # Update lead status if linked
        if self.lead:
            self.update_lead_status()
    
    def update_lead_status(self):
        """Update linked lead status"""
        frappe.db.set_value("Lead", self.lead, "status", "Opportunity")
    
    def close_won(self):
        """Mark opportunity as closed won"""
        self.status = "Closed Won"
        self.probability = 100
        self.db_update()
        
        # Convert to customer if lead
        if self.lead:
            customer = self.convert_lead_to_customer()
            self.customer = customer
            self.db_update()
        
        frappe.msgprint(_("Opportunity {0} closed as won").format(self.name))
    
    def close_lost(self):
        """Mark opportunity as closed lost"""
        self.status = "Closed Lost"
        self.probability = 0
        self.db_update()
        
        frappe.msgprint(_("Opportunity {0} closed as lost").format(self.name))
    
    def convert_lead_to_customer(self):
        """Convert lead to customer"""
        if not self.lead:
            return None
        
        lead = frappe.get_doc("Lead", self.lead)
        
        # Create customer
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": lead.lead_name or lead.company_name,
            "customer_group": "All Customer Groups",
            "territory": lead.territory or "All Territories",
            "company": self.company,
        })
        customer.insert(ignore_permissions=True)
        
        # Update lead status
        frappe.db.set_value("Lead", self.lead, "status", "Converted")
        
        return customer.name


@frappe.whitelist()
def get_opportunity_pipeline(company=None):
    """Get opportunity pipeline for dashboard"""
    filters = {}
    if company:
        filters["company"] = company
    
    opportunities = frappe.get_all(
        "Opportunity",
        filters=filters,
        fields=["name", "customer_name", "expected_amount", "status", "probability", "expected_close_date"],
        order_by="expected_close_date asc"
    )
    
    # Group by status
    pipeline = {}
    for opp in opportunities:
        status = opp.status
        if status not in pipeline:
            pipeline[status] = []
        pipeline[status].append(opp)
    
    return pipeline


@frappe.whitelist()
def get_pipeline_summary(company=None):
    """Get pipeline summary for dashboard"""
    filters = {}
    if company:
        filters["company"] = company
    
    opportunities = frappe.get_all(
        "Opportunity",
        filters=filters,
        fields=["expected_amount", "probability", "status"]
    )
    
    total_value = 0
    weighted_value = 0
    
    for opp in opportunities:
        total_value += flt(opp.expected_amount)
        weighted_value += flt(opp.expected_amount) * flt(opp.probability) / 100
    
    return {
        "total_opportunities": len(opportunities),
        "total_value": total_value,
        "weighted_value": weighted_value
    }
