import frappe
from frappe.model.document import Document

from erpmax.utils.naming import sync_transaction_party_fields


class SalesInvoice(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.calculate_commission()

    def calculate_totals(self):
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.tax_amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        self.outstanding_amount = self.grand_total

    def calculate_commission(self):
        """Calculate commission amount based on distributor and commission rate"""
        if self.distributor and self.commission_rate:
            self.commission_amount = (self.total * self.commission_rate) / 100
        else:
            self.commission_amount = 0

    def on_submit(self):
        self.status = "Submitted"
        self.make_gl_entries()
        self.create_distributor_commission()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()

    def make_gl_entries(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        debit_to = customer.default_receivable_account
        income_account = None
        for item in self.items:
            income_account = item.income_account
            break

        entries = []
        if debit_to:
            entries.append({"account": debit_to, "debit": self.grand_total, "credit": 0})
        if income_account:
            entries.append({"account": income_account, "debit": 0, "credit": self.total})
        for tax in self.taxes:
            if tax.account_head:
                entries.append({"account": tax.account_head, "debit": 0, "credit": tax.tax_amount})

        for entry in entries:
            gl = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": entry["account"],
                "debit": entry["debit"],
                "credit": entry["credit"],
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": "Customer",
                "party": self.customer,
            })
            gl.flags.ignore_permissions = True
            gl.insert()

    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

    def create_distributor_commission(self):
        """Create distributor commission entry if distributor and commission rate are set"""
        if not self.distributor or not self.commission_rate or not self.commission_amount:
            return

        try:
            from erpmax.business_setup.doctype.distributor_commission.distributor_commission import (
                create_commission_for_invoice,
            )
            create_commission_for_invoice(self)
        except Exception as e:
            frappe.log_error(f"Failed to create distributor commission for {self.name}: {str(e)}")

    @frappe.whitelist()
    def create_transport_delivery(self):
        """Create Transport Delivery from Sales Invoice"""
        try:
            from erpmax.sales.doctype.transport_delivery.transport_delivery import (
                create_delivery_from_invoice,
            )
            delivery_name = create_delivery_from_invoice(self.name)
            self.db_set("delivery_status", "Ready for Pickup")
            return delivery_name
        except Exception as e:
            frappe.throw(f"Failed to create transport delivery: {str(e)}")
