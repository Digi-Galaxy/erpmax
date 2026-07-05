import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class StockEntry(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        self.calculate_totals()
        self.validate_items()
        self.validate_warehouses()

    def calculate_totals(self):
        self.total_qty = 0
        self.total_amount = 0
        for row in self.items:
            if row.qty and row.rate:
                row.amount = row.qty * row.rate
            self.total_qty += row.qty or 0
            self.total_amount += row.amount or 0

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required")
        for row in self.items:
            if not row.item_name:
                frappe.throw(f"Row #{row.idx}: Item Name is required")
            if not row.qty or row.qty <= 0:
                frappe.throw(f"Row #{row.idx}: Quantity must be greater than 0")

    def validate_warehouses(self):
        if self.stock_entry_type == "Material Receipt":
            if not self.to_warehouse:
                frappe.throw("Target warehouse is required for Material Receipt")
        elif self.stock_entry_type == "Material Issue":
            if not self.from_warehouse:
                frappe.throw("Source warehouse is required for Material Issue")
        elif self.stock_entry_type == "Material Transfer":
            if not self.from_warehouse or not self.to_warehouse:
                frappe.throw("Both source and target warehouses are required for Material Transfer")

    def on_submit(self):
        self.status = "Submitted"
        self.make_stock_ledger_entries()
        self.db_update()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_stock_ledger_entries()
        self.db_update()

    def make_stock_ledger_entries(self):
        for item in self.items:
            qty = item.qty or 0
            if self.stock_entry_type == "Material Receipt":
                actual_qty = qty
                warehouse = self.to_warehouse
            elif self.stock_entry_type == "Material Issue":
                actual_qty = -qty
                warehouse = self.from_warehouse
            elif self.stock_entry_type == "Material Transfer":
                # Out from source
                sle_out = frappe.get_doc({
                    "doctype": "Stock Ledger Entry",
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "warehouse": self.from_warehouse,
                    "posting_date": self.posting_date or nowdate(),
                    "posting_time": "00:00:00",
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "actual_qty": -qty,
                    "valuation_rate": item.rate or 0,
                    "stock_value": -(qty * (item.rate or 0)),
                })
                sle_out.flags.ignore_permissions = True
                sle_out.insert()

                # In to target
                actual_qty = qty
                warehouse = self.to_warehouse
            else:
                continue

            if self.stock_entry_type != "Material Transfer":
                sle = frappe.get_doc({
                    "doctype": "Stock Ledger Entry",
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "warehouse": warehouse,
                    "posting_date": self.posting_date or nowdate(),
                    "posting_time": "00:00:00",
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "actual_qty": actual_qty,
                    "valuation_rate": item.rate or 0,
                    "stock_value": actual_qty * (item.rate or 0),
                })
                sle.flags.ignore_permissions = True
                sle.insert()

    def make_reverse_stock_ledger_entries(self):
        existing = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for sle in existing:
            frappe.db.set_value("Stock Ledger Entry", sle.name, "is_cancelled", 1)
