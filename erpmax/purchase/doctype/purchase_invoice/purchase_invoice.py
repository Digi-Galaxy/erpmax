import frappe
from frappe.model.document import Document

from erpmax.utils.naming import sync_transaction_party_fields

class PurchaseInvoice(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        sync_transaction_party_fields(self)
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.tax_amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        self.outstanding_amount = self.grand_total
    def on_submit(self):
        self.status = "Submitted"
    def on_cancel(self):
        self.status = "Cancelled"

# Module-level hooks wrappers for doc_events

def validate(doc, method):
    pass

def on_submit(doc, method):
    pass

def on_cancel(doc, method):
    pass

def get_permission_query_conditions(user, doctype=None):
    return ""
