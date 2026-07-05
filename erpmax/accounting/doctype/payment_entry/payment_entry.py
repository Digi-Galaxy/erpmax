import frappe
from frappe.model.document import Document

from erpmax.utils.naming import sync_transaction_party_fields


class PaymentEntry(Document):
    def validate(self):
        sync_transaction_party_fields(self)
        self.validate_references()
        self.calculate_totals()
        self.validate_totals()

    def validate_references(self):
        party_type_map = {"Customer": "Customer", "Supplier": "Supplier", "Partner Account": "Partner Account"}
        if self.party_type and self.party_type not in party_type_map:
            frappe.throw(f"Invalid party type: {self.party_type}")

        if self.references:
            for ref in self.references:
                if ref.allocated_amount and ref.allocated_amount > ref.outstanding_amount:
                    frappe.throw(
                        f"Row #{ref.idx}: Allocated amount {ref.allocated_amount} "
                        f"exceeds outstanding {ref.outstanding_amount} on {ref.reference_doctype} {ref.reference_name}"
                    )

    def calculate_totals(self):
        self.total_allocated_amount = sum(
            (row.allocated_amount or 0) for row in (self.references or [])
        )
        self.unallocated_amount = (self.paid_amount or 0) - self.total_allocated_amount
        self.difference_amount = (self.paid_amount or 0) - (self.received_amount or 0)

    def validate_totals(self):
        if self.total_allocated_amount > (self.paid_amount or 0):
            frappe.throw(
                f"Total allocated amount {self.total_allocated_amount} "
                f"cannot exceed paid amount {self.paid_amount}"
            )

        if self.references and self.total_allocated_amount <= 0:
            frappe.throw("Please allocate at least one reference invoice")

        if not self.references and self.unallocated_amount > 0:
            frappe.throw(
                "Unallocated amount exists but no references added. "
                "Please add references or clear the unallocated amount."
            )

    def on_submit(self):
        self.make_gl_entries()
        self.update_invoice_outstanding()

    def on_cancel(self):
        self.make_reverse_gl_entries()
        self.update_invoice_outstanding()

    def make_gl_entries(self):
        gl_entries = []

        if self.payment_type == "Receive":
            gl_entries.append({
                "account": self.paid_to,
                "debit": self.received_amount,
                "credit": 0,
                "party_type": self.party_type,
                "party": self.party,
            })
            gl_entries.append({
                "account": self.paid_from,
                "debit": 0,
                "credit": self.paid_amount,
            })
        elif self.payment_type == "Pay":
            gl_entries.append({
                "account": self.paid_from,
                "debit": 0,
                "credit": self.paid_amount,
                "party_type": self.party_type,
                "party": self.party,
            })
            gl_entries.append({
                "account": self.paid_to,
                "debit": self.received_amount,
                "credit": 0,
            })
        elif self.payment_type == "Internal Transfer":
            gl_entries.append({
                "account": self.paid_from,
                "debit": 0,
                "credit": self.paid_amount,
            })
            gl_entries.append({
                "account": self.paid_to,
                "debit": self.received_amount,
                "credit": 0,
            })

        for entry in gl_entries:
            gl = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": entry["account"],
                "debit": entry["debit"],
                "credit": entry["credit"],
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": entry.get("party_type"),
                "party": entry.get("party"),
            })
            gl.flags.ignore_permissions = True
            gl.insert()

    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

    def update_invoice_outstanding(self):
        if not self.references:
            return

        for ref in self.references:
            if not ref.reference_doctype or not ref.reference_name:
                continue

            if ref.reference_doctype not in ("Sales Invoice", "Purchase Invoice"):
                continue

            invoice = frappe.get_doc(ref.reference_doctype, ref.reference_name)
            paid_amount = self.get_paid_amount_for_invoice(ref)
            invoice.outstanding_amount = invoice.grand_total - paid_amount

            if invoice.outstanding_amount <= 0:
                invoice.outstanding_amount = 0
                invoice.status = "Paid"
            elif invoice.outstanding_amount < invoice.grand_total:
                invoice.status = "Partly Paid"
            else:
                invoice.status = "Submitted"

            invoice.flags.ignore_permissions = True
            invoice.flags.ignore_validate_update_after_submit = True
            invoice.db_update()

        frappe.db.commit()

    def get_paid_amount_for_invoice(self, ref):
        filters = {
            "reference_doctype": ref.reference_doctype,
            "reference_name": ref.reference_name,
            "docstatus": 1,
            "name": ["!=", self.name],
        }

        if self.payment_type == "Receive":
            filters["party_type"] = self.party_type
            filters["party"] = self.party

        paid = frappe.db.get_value(
            "Payment Entry Reference",
            filters,
            "sum(allocated_amount)",
        ) or 0

        if self.docstatus == 1:
            paid += ref.allocated_amount or 0
        elif self.docstatus == 2:
            paid -= ref.allocated_amount or 0

        return paid


@frappe.whitelist()
def get_outstanding_invoices(party_type, party, company):
    if not party_type or not party or not company:
        frappe.throw("Party type, party, and company are required")

    doctype = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
    party_field = "customer" if party_type == "Customer" else "supplier"

    invoices = frappe.get_all(
        doctype,
        filters={
            party_field: party,
            "company": company,
            "docstatus": 1,
            "outstanding_amount": [">", 0],
        },
        fields=["name", "grand_total", "outstanding_amount", "posting_date", "due_date"],
        order_by="posting_date asc",
    )

    return invoices


@frappe.whitelist()
def get_party_balance(party_type, party, company):
    if not party_type or not party or not company:
        frappe.throw("Party type, party, and company are required")

    filters = {
        "party_type": party_type,
        "party": party,
        "company": company,
        "is_cancelled": 0,
    }

    result = frappe.db.get_value(
        "GL Entry",
        filters,
        ["sum(debit)", "sum(credit)"],
    )

    debit = result[0] or 0
    credit = result[1] or 0
    balance = debit - credit

    return {
        "debit": debit,
        "credit": credit,
        "balance": balance,
    }
