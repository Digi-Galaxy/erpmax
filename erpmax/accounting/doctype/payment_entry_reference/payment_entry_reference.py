import frappe
from frappe.model.document import Document


class PaymentEntryReference(Document):
    def validate(self):
        if not self.reference_doctype or not self.reference_name:
            frappe.throw("Reference Doctype and Reference Name are required")

        if self.reference_doctype not in ("Sales Invoice", "Purchase Invoice", "Journal Entry"):
            frappe.throw("Reference must be Sales Invoice, Purchase Invoice, or Journal Entry")

        ref = frappe.get_doc(self.reference_doctype, self.reference_name)
        if ref.docstatus != 1:
            frappe.throw(f"{self.reference_doctype} {self.reference_name} is not submitted")

        if self.reference_doctype in ("Sales Invoice", "Purchase Invoice"):
            self.total_amount = ref.grand_total
            self.outstanding_amount = ref.outstanding_amount

        if self.allocated_amount and self.allocated_amount > 0:
            if self.allocated_amount > self.outstanding_amount:
                frappe.throw(
                    f"Allocated amount {self.allocated_amount} exceeds outstanding amount {self.outstanding_amount}"
                )
        else:
            frappe.throw("Allocated amount must be greater than 0")
