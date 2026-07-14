
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class Settlement(Document):
    def validate(self):
        self._ensure_required()
        self._ensure_posting_date()
        self._compute_summary_fields()
        self._validate_allocations()

    def _ensure_required(self):
        if not self.company:
            frappe.throw("Company is required")
        if not self.customer:
            frappe.throw("Customer is required")
        if not self.supplier:
            frappe.throw("Supplier is required")
        if not self.customer_receivable_account:
            frappe.throw("Customer Receivable Account is required")
        if not self.supplier_payable_account:
            frappe.throw("Supplier Payable Account is required")

    def _ensure_posting_date(self):
        if not self.posting_date:
            self.posting_date = nowdate()

    def _validate_allocations(self):
        total_cust = sum(d.allocate_amount or 0 for d in self.customer_allocations)
        total_supp = sum(d.allocate_amount or 0 for d in self.supplier_allocations)

        for d in self.customer_allocations:
            if not d.sales_invoice:
                continue
            si = frappe.get_doc("Sales Invoice", d.sales_invoice)
            if si.docstatus != 1:
                frappe.throw("Sales Invoice " + d.sales_invoice + " is not submitted")
            if d.allocate_amount > si.outstanding_amount:
                frappe.throw("Allocation exceeds outstanding for " + d.sales_invoice)

        for d in self.supplier_allocations:
            if not d.purchase_invoice:
                continue
            pi = frappe.get_doc("Purchase Invoice", d.purchase_invoice)
            if pi.docstatus != 1:
                frappe.throw("Purchase Invoice " + d.purchase_invoice + " is not submitted")
            if d.allocate_amount > pi.outstanding_amount:
                frappe.throw("Allocation exceeds outstanding for " + d.purchase_invoice)

        if total_cust > self.paid_amount:
            frappe.throw("Total customer allocation exceeds paid amount")
        if total_supp > self.paid_amount:
            frappe.throw("Total supplier allocation exceeds paid amount")

    def _compute_summary_fields(self):
        self.total_customer_allocated = sum(d.allocate_amount or 0 for d in self.customer_allocations)
        self.total_supplier_allocated = sum(d.allocate_amount or 0 for d in self.supplier_allocations)
        self.difference = self.total_customer_allocated - self.total_supplier_allocated
        self.settlement_amount = self.paid_amount

    def on_submit(self):
        if self.journal_entry:
            return
        je = self._make_journal_entry()
        self.db_set("journal_entry", je.name)

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            if je.docstatus == 1:
                je.cancel()
            self.db_set("journal_entry", None)

    def _make_journal_entry(self):
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = self.company
        je.posting_date = self.posting_date
        je.remark = "Settlement: " + self.customer + " -> " + self.supplier + " (" + self.name + ")"

        for d in self.supplier_allocations:
            je.append("accounts", {
                "account": self.supplier_payable_account,
                "party_type": "Supplier",
                "party": self.supplier,
                "debit_in_account_currency": d.allocate_amount,
                "credit_in_account_currency": 0,
                "reference_type": "Purchase Invoice",
                "reference_name": d.purchase_invoice,
            })

        supp_allocated = sum(d.allocate_amount or 0 for d in self.supplier_allocations)
        if self.paid_amount > supp_allocated:
            advance = self.paid_amount - supp_allocated
            if not self.supplier_advance_account:
                frappe.throw("Supplier Advance Account is required for unallocated amount")
            je.append("accounts", {
                "account": self.supplier_advance_account,
                "debit_in_account_currency": advance,
                "credit_in_account_currency": 0,
            })

        for d in self.customer_allocations:
            je.append("accounts", {
                "account": self.customer_receivable_account,
                "party_type": "Customer",
                "party": self.customer,
                "debit_in_account_currency": 0,
                "credit_in_account_currency": d.allocate_amount,
                "reference_type": "Sales Invoice",
                "reference_name": d.sales_invoice,
            })

        cust_allocated = sum(d.allocate_amount or 0 for d in self.customer_allocations)
        if self.paid_amount > cust_allocated:
            advance = self.paid_amount - cust_allocated
            if not self.customer_advance_account:
                frappe.throw("Customer Advance Account is required for unallocated amount")
            je.append("accounts", {
                "account": self.customer_advance_account,
                "debit_in_account_currency": 0,
                "credit_in_account_currency": advance,
            })

        je.flags.ignore_permissions = True
        je.insert()
        je.submit()
        return je
