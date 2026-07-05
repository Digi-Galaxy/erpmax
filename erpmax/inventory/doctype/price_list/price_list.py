import frappe
from frappe.model.document import Document


class PriceList(Document):
    def validate(self):
        self.validate_currency()

    def validate_currency(self):
        if self.currency:
            exists = frappe.db.exists("Price List", {
                "currency": self.currency,
                "name": ["!=", self.name],
            })
            if exists:
                frappe.throw(f"A price list with currency {self.currency} already exists")

    def on_update(self):
        self.update_item_prices()

    def update_item_prices(self):
        prices = frappe.get_all("Item Price", filters={
            "price_list": self.name,
        }, fields=["name", "item_code", "price_list"])
        for price in prices:
            frappe.db.set_value("Item Price", price.name, "price_list_name", self.name)

    @frappe.whitelist()
    def get_items(self):
        items = frappe.get_all("Item Price", filters={
            "price_list": self.name,
        }, fields=["item_code", "item_name", "price_list", "price_list_rate", "currency"])
        return items
