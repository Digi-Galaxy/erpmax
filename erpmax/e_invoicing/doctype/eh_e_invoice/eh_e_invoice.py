import frappe
from frappe.model.document import Document


class EHEInvoice(Document):
    def before_submit(self):
        if self.status not in ("Submitted", "Accepted", "Cleared"):
            frappe.throw(
                "Cannot submit e-invoice with status: {0}. Must be Submitted/Accepted/Cleared.".format(
                    self.status
                )
            )
