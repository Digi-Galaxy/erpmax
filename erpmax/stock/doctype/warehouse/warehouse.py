import frappe
from frappe.model.document import Document


class Warehouse(Document):
    def validate(self):
        self.validate_parent()
        self.set_abbr()

    def validate_parent(self):
        if self.parent_warehouse:
            parent = frappe.get_doc("Warehouse", self.parent_warehouse)
            if parent.company and parent.company != self.company:
                frappe.throw("Parent warehouse must belong to the same company")

    def set_abbr(self):
        if not self.warehouse_abbr and self.warehouse_name:
            from erpmax.utils.naming import make_abbreviation
            self.warehouse_abbr = make_abbreviation(self.warehouse_name, fallback="WH")

    def on_update(self):
        self.update_stock_balance()

    def update_stock_balance(self):
        balance = frappe.db.get_value("Stock Ledger Entry", {
            "warehouse": self.name,
            "is_cancelled": 0,
        }, "sum(actual_qty)") or 0
        self.current_stock = balance
        self.db_update()
