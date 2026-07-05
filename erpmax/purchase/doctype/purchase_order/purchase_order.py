import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

from erpmax.utils.naming import sync_transaction_party_fields


class PurchaseOrder(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.validate_items()
        self.validate_party()
        self.validate_dates()
        self.set_accounts()

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
        self.per_received = 0
        self.per_billed = 0

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required")
        for row in self.items:
            if not row.item_name:
                frappe.throw(f"Row #{row.idx}: Item Name is required")
            if not row.qty or row.qty <= 0:
                frappe.throw(f"Row #{row.idx}: Quantity must be greater than 0")

    def validate_party(self):
        if not self.supplier:
            frappe.throw("Supplier is required")
        supplier = frappe.get_cached_doc("Supplier", self.supplier)
        if supplier.disabled:
            frappe.throw(f"Supplier {self.supplier} is disabled")

    def validate_dates(self):
        if self.schedule_date and self.order_date:
            if getdate(self.schedule_date) < getdate(self.order_date):
                frappe.throw("Required Date cannot be before Order Date")

    def set_accounts(self):
        if not self.buying_price_list:
            self.buying_price_list = "Standard Buying"
        if not self.currency:
            self.currency = "PKR"

    def on_submit(self):
        self.status = "Submitted"
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_update()

    @frappe.whitelist()
    def create_purchase_receipt(self):
        try:
            pr = frappe.get_doc({
                "doctype": "Purchase Receipt",
                "supplier": self.supplier,
                "posting_date": nowdate(),
                "company": self.company,
                "purchase_order": self.name,
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "warehouse": item.warehouse,
                    "expense_account": item.expense_account,
                } for item in self.items],
            })
            pr.insert()
            return pr.name
        except Exception as e:
            frappe.throw(f"Failed to create purchase receipt: {str(e)}")

    @frappe.whitelist()
    def create_purchase_invoice(self):
        try:
            pi = frappe.get_doc({
                "doctype": "Purchase Invoice",
                "supplier": self.supplier,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 30),
                "company": self.company,
                "purchase_order": self.name,
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "expense_account": item.expense_account,
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
            frappe.throw(f"Failed to create purchase invoice: {str(e)}")

    def update_received_qty(self):
        received = 0
        for item in self.items:
            received += item.received_qty or 0
        if self.total_qty:
            self.per_received = (received / self.total_qty) * 100
        self.db_update()
