import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

from erpmax.utils.naming import sync_transaction_party_fields


class DeliveryNote(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.validate_items()
        self.validate_party()

    def calculate_totals(self):
        self.total = 0
        self.total_qty = 0
        for row in self.items:
            if row.qty and row.rate:
                row.amount = row.qty * row.rate
            self.total += row.amount or 0
            self.total_qty += row.qty or 0

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required")

    def validate_party(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def on_submit(self):
        self.status = "Submitted"
        self.update_sales_order_delivery()
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.revert_sales_order_delivery()
        self.db_update()

    def update_sales_order_delivery(self):
        if self.sales_order:
            so = frappe.get_doc("Sales Delivery Note", self.sales_order)
            for item in self.items:
                for so_item in so.items:
                    if so_item.item_name == item.item_name:
                        so_item.delivered_qty = (so_item.delivered_qty or 0) + item.qty
            so.update_delivery_status()

    def revert_sales_order_delivery(self):
        if self.sales_order:
            so = frappe.get_doc("Sales Order", self.sales_order)
            for item in self.items:
                for so_item in so.items:
                    if so_item.item_name == item.item_name:
                        so_item.delivered_qty = (so_item.delivered_qty or 0) - item.qty
            so.update_delivery_status()

    @frappe.whitelist()
    def create_sales_invoice(self, remarks=None):
        """Create Sales Invoice from Delivery Note with optional dynamic remarks"""
        try:
            si = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "posting_date": nowdate(),
                "company": self.company,
                "delivery_note": self.name,
                "remarks": remarks or f"Invoice for Delivery Note {self.name}",
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                } for item in self.items],
            })
            si.insert()
            return si.name
        except Exception as e:
            frappe.throw(f"Failed to create sales invoice: {str(e)}")
