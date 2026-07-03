import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class TransportDelivery(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        if self.sales_invoice:
            self.fetch_invoice_details()

    def fetch_invoice_details(self):
        """Fetch customer and items from Sales Invoice"""
        invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
        self.customer = invoice.customer
        self.distributor = invoice.distributor
        self.company = invoice.company
        
        if not self.items:
            for item in invoice.items:
                self.append("items", {
                    "item": item.item,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "uom": item.uom,
                    "delivered_qty": 0,
                    "returned_qty": 0,
                    "status": "Pending"
                })

    def on_submit(self):
        self.status = "Ready for Pickup"

    def on_cancel(self):
        self.status = "Cancelled"

    @frappe.whitelist()
    def mark_picked(self):
        """Mark delivery as picked"""
        self.status = "Picked"
        self.picked_at = now_datetime()
        self.picked_by = frappe.session.user
        self.save()

    @frappe.whitelist()
    def mark_shipped(self):
        """Mark delivery as in transit"""
        if self.status != "Picked":
            frappe.throw("Delivery must be picked before shipping")
        self.status = "In Transit"
        self.shipped_at = now_datetime()
        self.shipped_by = frappe.session.user
        self.save()

    @frappe.whitelist()
    def mark_delivered(self, delivered_items=None):
        """Mark delivery as delivered with item quantities"""
        if self.status not in ["Picked", "In Transit"]:
            frappe.throw("Delivery must be picked or in transit before marking delivered")
        
        if delivered_items:
            for item_data in delivered_items:
                for item in self.items:
                    if item.item == item_data.get("item"):
                        item.delivered_qty = item_data.get("delivered_qty", item.qty)
                        item.returned_qty = item_data.get("returned_qty", 0)
                        if item.returned_qty > 0:
                            item.status = "Returned"
                        elif item.delivered_qty >= item.qty:
                            item.status = "Delivered"
                        elif item.delivered_qty > 0:
                            item.status = "Partially Delivered"
                        break
        else:
            for item in self.items:
                item.delivered_qty = item.qty
                item.status = "Delivered"
        
        self.status = "Delivered"
        self.delivered_at = now_datetime()
        self.delivered_by = frappe.session.user
        self.save()
        self.update_sales_invoice_status()

    def update_sales_invoice_status(self):
        """Update Sales Invoice with delivery status"""
        if self.sales_invoice:
            invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
            invoice.db_set("delivery_status", "Delivered")
            invoice.db_set("delivery_note", self.name)


