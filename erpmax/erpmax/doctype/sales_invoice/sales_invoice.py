import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
    def before_save(self):
        if self.customer:
            settings = frappe.get_single("ERPMax Settings")
            if settings.show_previous_balance:
                self.set_previous_balance()

    def onload(self):
        if self.customer and self.get("__islocal"):
            settings = frappe.get_single("ERPMax Settings")
            if settings.show_previous_balance:
                self.set_previous_balance()

    def set_previous_balance(self):
        balance = frappe.db.sql("""
            SELECT COALESCE(SUM(outstanding_amount), 0)
            FROM `tabSales Invoice`
            WHERE customer = %s
                AND docstatus = 1
                AND name != %s
                AND outstanding_amount > 0
        """, (self.customer, self.name or ""))

        self.previous_balance = balance[0][0] if balance else 0

    def on_submit(self):
        pass

    def on_cancel(self):
        pass
