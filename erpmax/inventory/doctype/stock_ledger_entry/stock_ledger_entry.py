import frappe
from frappe.model.document import Document


class StockLedgerEntry(Document):
    def validate(self):
        self.validate_warehouse()
        self.calculate_stock_value()

    def validate_warehouse(self):
        if not self.warehouse:
            frappe.throw("Warehouse is required")

    def calculate_stock_value(self):
        if self.actual_qty and self.valuation_rate:
            self.stock_value = self.actual_qty * self.valuation_rate

    def on_update(self):
        self.update_warehouse_stock()

    def update_warehouse_stock(self):
        if self.warehouse:
            balance = frappe.db.get_value("Stock Ledger Entry", {
                "warehouse": self.warehouse,
                "is_cancelled": 0,
            }, "sum(actual_qty)") or 0
            frappe.db.set_value("Warehouse", self.warehouse, "current_stock", balance)
