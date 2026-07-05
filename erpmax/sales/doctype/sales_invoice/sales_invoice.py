import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, flt

from erpmax.utils.naming import sync_transaction_party_fields


class SalesInvoice(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.calculate_commission()
        self.calculate_discount()
        self.validate_addon_settings()

    def calculate_totals(self):
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.tax_amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        if not self.outstanding_amount:
            self.outstanding_amount = self.grand_total

    def calculate_commission(self):
        if self.distributor and self.commission_rate:
            self.commission_amount = (self.total * self.commission_rate) / 100
        else:
            self.commission_amount = 0

    def calculate_discount(self):
        if self.line_discount_percent:
            self.discount_amount = self.total * (self.line_discount_percent / 100)
        elif self.invoice_discount_percent:
            self.discount_amount = self.grand_total * (self.invoice_discount_percent / 100)
        else:
            self.discount_amount = 0
        self.net_discounted_total = self.grand_total - self.discount_amount

    def validate_addon_settings(self):
        try:
            settings = frappe.get_single("Sales Invoice Addon Settings")
            if self.allow_partial_payment and settings.min_payment_percent:
                min_amount = self.grand_total * (settings.min_payment_percent / 100)
                self.min_payment_amount = min_amount
            if settings.max_discount_percent and self.invoice_discount_percent:
                if self.invoice_discount_percent > settings.max_discount_percent:
                    frappe.throw(_("Invoice discount cannot exceed {0}%").format(settings.max_discount_percent))
            if settings.payment_suggestions:
                self.calculate_payment_suggestions()
        except:
            pass

    def calculate_payment_suggestions(self):
        outstanding = self.outstanding_amount or self.grand_total
        self.payment_suggestion_1 = outstanding * 0.25
        self.payment_suggestion_2 = outstanding * 0.50
        self.payment_suggestion_3 = outstanding * 0.75

    def create_distributor_commission(self):
        if not self.distributor:
            return

    def on_submit(self):
        self.status = "Submitted"
        self.make_gl_entries()
        self.create_distributor_commission()
        self.update_outstanding_info()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()
        self.revert_outstanding()

    def update_outstanding_info(self):
        try:
            customer_outstanding = frappe.db.get_value(
                "Sales Invoice",
                {
                    "customer": self.customer,
                    "outstanding_amount": [">", 0],
                    "docstatus": 1,
                    "name": ["!=", self.name]
                },
                "sum(outstanding_amount)"
            ) or 0
            total_outstanding = customer_outstanding + (self.outstanding_amount or 0)
            overdue = self.due_date and getdate(self.due_date) < getdate()
            frappe.db.set_value("Customer", self.customer, {
                "outstanding_balance": total_outstanding,
                "outstanding_status": "Overdue" if overdue else "Current",
                "outstanding_days_overdue": (getdate() - getdate(self.due_date)).days if overdue else 0
            })
        except Exception:
            pass

    def make_gl_entries(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        debit_to = customer.default_receivable_account
        income_account = None
        for item in self.items:
            income_account = item.income_account or frappe.db.get_value("Item", {"item_name": item.item_name}, "income_account")
            break

        entries = []
        if debit_to:
            entries.append({"account": debit_to, "debit": self.grand_total, "credit": 0})
        if income_account:
            entries.append({"account": income_account, "debit": 0, "credit": self.total})
        for tax in self.taxes:
            if tax.account_head:
                entries.append({"account": tax.account_head, "debit": 0, "credit": tax.tax_amount})

        net_ct_adjustment = 0
        for ct in self.get("applied_commercial_terms", []):
            amt = flt(ct.calculated_amount)
            if not amt or not ct.account:
                continue
            rule_type = ct.rule_type
            if rule_type == "Receivable Hold":
                entries.append({"account": ct.account, "debit": amt, "credit": 0})
                entries.append({"account": debit_to, "debit": 0, "credit": amt})
                net_ct_adjustment -= amt
            elif rule_type == "Deduction":
                entries.append({"account": ct.account, "debit": amt, "credit": 0})
                entries.append({"account": debit_to, "debit": 0, "credit": amt})
                net_ct_adjustment -= amt
            elif rule_type == "Addition":
                entries.append({"account": debit_to, "debit": amt, "credit": 0})
                entries.append({"account": ct.account, "debit": 0, "credit": amt})
                net_ct_adjustment += amt
            elif rule_type == "Payable Hold":
                entries.append({"account": debit_to, "debit": 0, "credit": amt})
                entries.append({"account": ct.account, "debit": 0, "credit": amt})

        if net_ct_adjustment:
            self.outstanding_amount = flt(self.outstanding_amount) + net_ct_adjustment
            self.db_set("outstanding_amount", self.outstanding_amount)

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
            "voucher_no": self.name,
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

    def revert_outstanding(self):
        self.outstanding_amount = self.grand_total
        self.status = "Submitted"
        self.db_update()

    def get_payments_received(self):
        filters = {
            "reference_doctype": "Sales Invoice",
            "reference_name": self.name,
            "docstatus": 1,
        }
        paid = frappe.db.get_value(
            "Payment Entry Reference",
            filters,
            "sum(allocated_amount)",
        ) or 0
        return paid

    @frappe.whitelist()
    def create_transport_delivery(self):
        try:
            from erpmax.sales.doctype.transport_delivery.transport_delivery import (
                create_delivery_from_invoice,
            )
            delivery_name = create_delivery_from_invoice(self.name)
            self.db_set("delivery_status", "Ready for Pickup")
            return delivery_name
        except Exception as e:
            frappe.throw(f"Failed to create transport delivery: {str(e)}")

    @frappe.whitelist()
    def fetch_outstanding_balance(self):
        customer_outstanding = frappe.db.get_value(
            "Sales Invoice",
            {
                "customer": self.customer,
                "outstanding_amount": [">", 0],
                "docstatus": 1,
                "name": ["!=", self.name]
            },
            "sum(outstanding_amount)"
        ) or 0
        self.outstanding_balance = customer_outstanding
        self.outstanding_status = "Overdue" if self.due_date and self.due_date < getdate() else "Current"
        self.outstanding_days_overdue = max(0, (getdate() - self.due_date).days) if self.due_date and self.due_date < getdate() else 0
        if self.outstanding_days_overdue > 30:
            self.outstanding_warning = "WARNING: Customer has significant overdue balance"
        self.db_update()
        return {
            "outstanding_balance": self.outstanding_balance,
            "outstanding_status": self.outstanding_status,
            "outstanding_days_overdue": self.outstanding_days_overdue,
            "outstanding_warning": self.outstanding_warning
        }

    @frappe.whitelist()
    def get_payment_suggestions(self):
        outstanding = self.outstanding_amount or self.grand_total
        suggestions = [
            {"label": "Full Payment", "amount": outstanding},
            {"label": "25% Payment", "amount": outstanding * 0.25},
            {"label": "50% Payment", "amount": outstanding * 0.50},
            {"label": "75% Payment", "amount": outstanding * 0.75},
        ]
        return suggestions

    @frappe.whitelist()
    def apply_partial_payment(self, amount):
        if amount <= 0:
            frappe.throw(_("Payment amount must be greater than 0"))
        if amount > self.outstanding_amount:
            frappe.throw(_("Payment amount cannot exceed outstanding amount"))
        try:
            settings = frappe.get_single("Sales Invoice Addon Settings")
            if settings.allow_partial_payment and settings.min_payment_percent:
                min_amount = self.grand_total * (settings.min_payment_percent / 100)
                if amount < min_amount:
                    frappe.throw(_("Payment amount must be at least {0}% ({1})").format(
                        settings.min_payment_percent, min_amount
                    ))
        except:
            pass
        self.outstanding_amount = self.outstanding_amount - amount
        if self.outstanding_amount <= 0:
            self.status = "Paid"
        else:
            self.status = "Partly Paid"
        self.db_update()
        return {
            "outstanding_amount": self.outstanding_amount,
            "status": self.status
        }
