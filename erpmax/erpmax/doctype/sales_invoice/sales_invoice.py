import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
    def before_save(self):
        pass
    def on_submit(self):
        pass
    def on_cancel(self):
        pass
