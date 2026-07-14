# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class CountryCompliance(Document):
    def validate(self):
        self.validate_country_code()
    
    def validate_country_code(self):
        """Validate country code format"""
        if self.country and len(self.country) != 2:
            frappe.throw(_("Country code must be 2 characters (ISO 3166-1 alpha-2)"))


# Default country compliance configurations
DEFAULT_COUNTRY_COMPLIANCES = {
    "PK": {
        "country_name": "Pakistan",
        "compliance_type": "FBR",
        "enable_einvoicing": 1,
        "einv_provider": "FBR",
        "enable_vat": 0,
        "tax_invoice_format": "Standard",
        "digital_signature": 0,
        "qr_code_required": 1,
        "auto_submit": 1,
        "default_currency": "PKR",
        "currency_symbol": "Rs"
    },
    "SA": {
        "country_name": "Saudi Arabia",
        "compliance_type": "ZATCA",
        "enable_einvoicing": 1,
        "einv_provider": "ZATCA",
        "enable_vat": 1,
        "vat_rate": 15,
        "tax_invoice_format": "Digital",
        "digital_signature": 1,
        "qr_code_required": 1,
        "auto_submit": 1,
        "default_currency": "SAR",
        "currency_symbol": "SR"
    },
    "AE": {
        "country_name": "United Arab Emirates",
        "compliance_type": "UAE",
        "enable_einvoicing": 1,
        "einv_provider": "UAE FTA",
        "enable_vat": 1,
        "vat_rate": 5,
        "tax_invoice_format": "Digital",
        "digital_signature": 0,
        "qr_code_required": 1,
        "auto_submit": 1,
        "default_currency": "AED",
        "currency_symbol": "AED"
    },
    "IN": {
        "country_name": "India",
        "compliance_type": "GST",
        "enable_einvoicing": 1,
        "einv_provider": "Custom",
        "enable_vat": 0,
        "tax_invoice_format": "Standard",
        "digital_signature": 0,
        "qr_code_required": 1,
        "auto_submit": 1,
        "default_currency": "INR",
        "currency_symbol": "₹"
    },
    "GB": {
        "country_name": "United Kingdom",
        "compliance_type": "VAT",
        "enable_einvoicing": 0,
        "enable_vat": 1,
        "vat_rate": 20,
        "tax_invoice_format": "Standard",
        "digital_signature": 0,
        "qr_code_required": 0,
        "auto_submit": 0,
        "default_currency": "GBP",
        "currency_symbol": "£"
    },
    "US": {
        "country_name": "United States",
        "compliance_type": "Standard",
        "enable_einvoicing": 0,
        "enable_vat": 0,
        "tax_invoice_format": "Standard",
        "digital_signature": 0,
        "qr_code_required": 0,
        "auto_submit": 0,
        "default_currency": "USD",
        "currency_symbol": "$"
    }
}


def get_country_compliance(country_code):
    """Get compliance settings for a country"""
    compliance = frappe.db.get_value(
        "Country Compliance",
        {"country": country_code},
        "*",
        as_dict=True
    )
    
    if compliance:
        return compliance
    
    # Return default if not configured
    if country_code in DEFAULT_COUNTRY_COMPLIANCES:
        return DEFAULT_COUNTRY_COMPLIANCES[country_code]
    
    return None


def setup_country_compliance(country_code):
    """Setup compliance for a country"""
    if country_code not in DEFAULT_COUNTRY_COMPLIANCES:
        return False
    
    config = DEFAULT_COUNTRY_COMPLIANCES[country_code]
    
    # Check if already exists
    existing = frappe.db.get_value("Country Compliance", {"country": country_code})
    if existing:
        return True
    
    # Create compliance settings
    try:
        compliance = frappe.get_doc({
            "doctype": "Country Compliance",
            "country": country_code,
            "country_name": config["country_name"],
            "compliance_type": config["compliance_type"],
            "enable_einvoicing": config.get("enable_einvoicing", 0),
            "einv_provider": config.get("einv_provider", ""),
            "enable_vat": config.get("enable_vat", 0),
            "vat_rate": config.get("vat_rate", 0),
            "tax_invoice_format": config.get("tax_invoice_format", "Standard"),
            "digital_signature": config.get("digital_signature", 0),
            "qr_code_required": config.get("qr_code_required", 0),
            "auto_submit": config.get("auto_submit", 0),
            "default_currency": config.get("default_currency", ""),
            "currency_symbol": config.get("currency_symbol", "")
        })
        compliance.insert(ignore_permissions=True)
        frappe.db.commit()
        return True
    except Exception as e:
        frappe.log_error(f"Failed to setup country compliance: {str(e)}")
        return False


def apply_country_defaults(company_name, country_code):
    """Apply country-specific defaults to a company"""
    compliance = get_country_compliance(country_code)
    if not compliance:
        return
    
    # Apply currency
    if compliance.get("default_currency"):
        frappe.db.set_value("Company", company_name, "default_currency", compliance["default_currency"])
    
    # Apply VAT settings
    if compliance.get("enable_vat"):
        frappe.db.set_value("Company", company_name, "enable_vat", 1)
        if compliance.get("vat_rate"):
            frappe.db.set_value("Company", company_name, "default_vat_rate", compliance["vat_rate"])
    
    # Apply e-invoicing settings
    if compliance.get("enable_einvoicing"):
        frappe.db.set_value("Company", company_name, "enable_einvoicing", 1)
        if compliance.get("einv_provider"):
            frappe.db.set_value("Company", company_name, "einv_provider", compliance["einv_provider"])
    
    frappe.db.commit()
