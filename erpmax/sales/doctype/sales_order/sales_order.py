import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

from erpmax.utils.naming import sync_transaction_party_fields


class SalesOrder(Document):
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
        self.per_delivered = 0
        self.per_billed = 0

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
        if self.delivery_date and self.transaction_date:
            if getdate(self.delivery_date) < getdate(self.transaction_date):
                frappe.throw("Delivery Date cannot be before Order Date")

    def on_submit(self):
        self.status = "Submitted"
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_update()

    @frappe.whitelist()
    def create_delivery_note(self, remarks=None):
        """Create Delivery Note from Sales Order with optional dynamic remarks"""
        try:
            dn = frappe.get_doc({
                "doctype": "Delivery Note",
                "customer": self.customer,
                "posting_date": nowdate(),
                "company": self.company,
                "sales_order": self.name,
                "remarks": remarks or f"Delivery for Sales Order {self.name}",
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "warehouse": item.warehouse,
                } for item in self.items],
            })
            dn.insert()
            return dn.name
        except Exception as e:
            frappe.throw(f"Failed to create delivery note: {str(e)}")

    @frappe.whitelist()
    def create_sales_invoice(self, remarks=None):
        """Create Sales Invoice from Sales Order with optional dynamic remarks"""
        try:
            si = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 30),
                "company": self.company,
                "sales_order": self.name,
                "remarks": remarks or f"Invoice for Sales Order {self.name}",
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

    @frappe.whitelist()
    def create_proforma_invoice(self, remarks=None):
        """Create Proforma Invoice from Sales Order with optional dynamic remarks"""
        try:
            pi = frappe.get_doc({
                "doctype": "Proforma Invoice",
                "customer": self.customer,
                "posting_date": nowdate(),
                "company": self.company,
                "sales_order": self.name,
                "remarks": remarks or f"Proforma for Sales Order {self.name}",
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

    def update_delivery_status(self):
        delivered = 0
        for item in self.items:
            delivered += item.delivered_qty or 0
        if self.total_qty:
            self.per_delivered = (delivered / self.total_qty) * 100
        self.db_update()
