import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

from erpmax.utils.naming import sync_transaction_party_fields


class Quotation(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.validate_items()
        self.validate_party()
        self.validate_dates()

    def calculate_totals(self):
        self.total = 0
        for row in self.items:
            if row.qty and row.rate:
                row.amount = row.qty * row.rate
            self.total += row.amount or 0

        self.tax_total = 0
        for row in self.taxes:
            if row.charge_type == "On Net Total" and row.rate:
                row.tax_amount = (self.total * row.rate) / 100
            self.tax_total += row.tax_amount or 0

        self.grand_total = self.total + self.tax_total

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required")
        for row in self.items:
            if not row.item_name:
                frappe.throw(f"Row #{row.idx}: Item Name is required")

    def validate_party(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def validate_dates(self):
        if self.valid_till and self.transaction_date:
            if getdate(self.valid_till) < getdate(self.transaction_date):
                frappe.throw("Valid Till cannot be before Transaction Date")

    def on_submit(self):
        self.status = "Submitted"
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_update()

    @frappe.whitelist()
    def create_sales_order(self, remarks=None):
        """Create Sales Order from Quotation with optional dynamic remarks"""
        try:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "customer": self.customer,
                "transaction_date": nowdate(),
                "delivery_date": add_days(nowdate(), 7),
                "company": self.company,
                "quotation": self.name,
                "remarks": remarks or f"Order from Quotation {self.name}",
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "income_account": item.income_account,
                } for item in self.items],
                "taxes": [{
                    "charge_type": tax.charge_type,
                    "account_head": tax.account_head,
                    "rate": tax.rate,
                    "tax_amount": tax.tax_amount,
                    "description": tax.description,
                } for tax in self.taxes],
            })
            so.insert()
            return so.name
        except Exception as e:
            frappe.throw(f"Failed to create sales order: {str(e)}")

    @frappe.whitelist()
    def create_proforma_invoice(self, remarks=None):
        """Create Proforma Invoice from Quotation with optional dynamic remarks

        User can create without submit and add remarks like:
        'Invoice for Month of July to Customer Name'
        """
        try:
            pi = frappe.get_doc({
                "doctype": "Proforma Invoice",
                "customer": self.customer,
                "posting_date": nowdate(),
                "company": self.company,
                "quotation": self.name,
                "remarks": remarks or f"Proforma for Quotation {self.name}",
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "income_account": item.income_account,
                } for item in self.items],
                "taxes": [{
                    "charge_type": tax.charge_type,
                    "account_head": tax.account_head,
                    "rate": tax.rate,
                    "tax_amount": tax.tax_amount,
                    "description": tax.description,
                } for tax in self.taxes],
            })
            pi.insert()
            return pi.name
        except Exception as e:
            frappe.throw(f"Failed to create proforma invoice: {str(e)}")

    @frappe.whitelist()
    def create_sales_invoice(self, remarks=None):
        """Create Sales Invoice directly from Quotation with optional dynamic remarks"""
        try:
            si = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 30),
                "company": self.company,
                "quotation": self.name,
                "remarks": remarks or f"Invoice for Quotation {self.name}",
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "income_account": item.income_account,
                } for item in self.items],
                "taxes": [{
                    "charge_type": tax.charge_type,
                    "account_head": tax.account_head,
                    "rate": tax.rate,
                    "tax_amount": tax.tax_amount,
                    "description": tax.description,
                } for tax in self.taxes],
            })
            si.insert()
            return si.name
        except Exception as e:
            frappe.throw(f"Failed to create sales invoice: {str(e)}")
