# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class CustomerAddonSettings(Document):
    def validate(self):
        self.validate_dunning_settings()
        self.validate_loyalty_settings()
    
    def validate_dunning_settings(self):
        if self.enable_dunning:
            if not self.dunning_days_before:
                frappe.throw(_("Days Before Dunning is required when Dunning is enabled"))
            if not self.dunning_method:
                frappe.throw(_("Dunning Method is required when Dunning is enabled"))
    
    def validate_loyalty_settings(self):
        if self.enable_loyalty_points:
            if not self.loyalty_program:
                frappe.throw(_("Loyalty Program Name is required when Loyalty Points is enabled"))
            if not self.loyalty_currency:
                frappe.throw(_("Loyalty Currency is required when Loyalty Points is enabled"))


def get_addon_settings():
    """Get customer addon settings"""
    try:
        return frappe.get_single("Customer Addon Settings")
    except:
        return None


def is_addon_enabled(addon_name):
    """Check if a specific addon is enabled"""
    settings = get_addon_settings()
    if not settings:
        return False
    
    addon_field = f"enable_{addon_name}"
    return getattr(settings, addon_field, False)
