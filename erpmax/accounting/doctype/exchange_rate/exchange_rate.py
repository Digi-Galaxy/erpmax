# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class ExchangeRate(Document):
    def validate(self):
        self.validate_currencies()
        self.validate_rate()
        self.validate_overlap()
    
    def validate_currencies(self):
        """Validate that from and to currencies are different"""
        if self.from_currency == self.to_currency:
            frappe.throw(_("From Currency and To Currency cannot be the same"))
    
    def validate_rate(self):
        """Validate exchange rate"""
        if flt(self.exchange_rate) <= 0:
            frappe.throw(_("Exchange Rate must be greater than 0"))
    
    def validate_overlap(self):
        """Check for overlapping exchange rates"""
        filters = {
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "company": self.company,
            "name": ["!=", self.name],
        }
        
        if self.valid_upto:
            filters["valid_from"] = ["<=", self.valid_upto]
        
        existing = frappe.get_all(
            "Exchange Rate",
            filters=filters,
            fields=["name", "valid_from", "valid_upto"]
        )
        
        for rate in existing:
            if rate.valid_upto is None or (self.valid_from <= rate.valid_upto):
                frappe.throw(
                    _("Exchange rate already exists for {0} to {1} starting from {2}").format(
                        self.from_currency, self.to_currency, rate.valid_from
                    )
                )


def get_exchange_rate(from_currency, to_currency, date=None, company=None):
    """
    Get exchange rate for currency conversion.
    
    Args:
        from_currency: Source currency
        to_currency: Target currency
        date: Date for exchange rate (default: today)
        company: Company filter
    
    Returns:
        float: Exchange rate or 1.0 if same currency
    """
    if from_currency == to_currency:
        return 1.0
    
    if not date:
        date = nowdate()
    
    filters = {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "valid_from": ["<=", date],
    }
    
    if company:
        filters["company"] = company
    
    # Get the most recent valid exchange rate
    rate = frappe.db.get_value(
        "Exchange Rate",
        filters,
        "exchange_rate",
        order_by="valid_from desc"
    )
    
    if rate:
        return flt(rate)
    
    # Try reverse rate
    reverse_rate = frappe.db.get_value(
        "Exchange Rate",
        {
            "from_currency": to_currency,
            "to_currency": from_currency,
            "valid_from": ["<=", date],
        },
        "exchange_rate",
        order_by="valid_from desc"
    )
    
    if reverse_rate:
        return 1.0 / flt(reverse_rate)
    
    # Default to 1.0 if no rate found
    return 1.0


def convert_currency(amount, from_currency, to_currency, date=None, company=None):
    """
    Convert amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency
        to_currency: Target currency
        date: Date for exchange rate
        company: Company filter
    
    Returns:
        float: Converted amount
    """
    if from_currency == to_currency:
        return flt(amount)
    
    rate = get_exchange_rate(from_currency, to_currency, date, company)
    return flt(amount) * rate


def get_currency_info(currency):
    """Get currency information"""
    return frappe.get_doc("Currency", currency)


@frappe.whitelist()
def get_exchange_rate_api(from_currency, to_currency, date=None, company=None):
    """API endpoint to get exchange rate"""
    rate = get_exchange_rate(from_currency, to_currency, date, company)
    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": rate,
        "date": date or nowdate()
    }


@frappe.whitelist()
def convert_currency_api(amount, from_currency, to_currency, date=None, company=None):
    """API endpoint to convert currency"""
    converted = convert_currency(amount, from_currency, to_currency, date, company)
    rate = get_exchange_rate(from_currency, to_currency, date, company)
    
    return {
        "original_amount": flt(amount),
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": rate,
        "converted_amount": flt(converted, 2)
    }


@frappe.whitelist()
def get_available_currencies():
    """Get list of available currencies"""
    currencies = frappe.get_all(
        "Currency",
        fields=["name", "currency_name", "enabled"],
        filters={"enabled": 1}
    )
    return currencies
