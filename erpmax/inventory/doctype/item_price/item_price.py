import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ItemPrice(Document):
    def validate(self):
        self.validate_price()
        self.validate_date_range()

    def validate_price(self):
        if self.price_list_rate and self.price_list_rate < 0:
            frappe.throw("Price List Rate cannot be negative")

    def validate_date_range(self):
        if self.valid_from and self.valid_upto:
            if getdate(self.valid_upto) < getdate(self.valid_from):
                frappe.throw("Valid Upto cannot be before Valid From")

    def on_update(self):
        self.update_price_list()

    def update_price_list(self):
        if self.price_list:
            frappe.db.set_value("Price List", self.price_list, "last_updated", frappe.utils.nowdate())

    @frappe.whitelist()
    def get_price(self, qty=1, date=None):
        """Get price for given quantity and date"""
        if not date:
            date = frappe.utils.nowdate()

        if self.valid_from and getdate(date) < getdate(self.valid_from):
            return 0

        if self.valid_upto and getdate(date) > getdate(self.valid_upto):
            return 0

        if self.min_qty and qty < self.min_qty:
            return 0

        return self.price_list_rate or 0
