import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class CreditNote(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        if not self.outstanding_amount:
            self.outstanding_amount = self.grand_total

    def on_submit(self):
        self.status = "Submitted"
        self.make_gl_entries()
        self.update_original_invoice()
        self.reverse_commission()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()
        self.revert_original_invoice()
        self.undo_reverse_commission()

    def make_gl_entries(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        debit_to = customer.default_receivable_account
        income_account = None
        for item in self.items:
            income_account = item.income_account
            break

        entries = []
        if debit_to:
            entries.append({"account": debit_to, "debit": 0, "credit": self.grand_total})
        if income_account:
            entries.append({"account": income_account, "debit": self.total, "credit": 0})
        for tax in self.taxes:
            if tax.account_head:
                entries.append({"account": tax.account_head, "debit": tax.amount, "credit": 0})

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

    def update_original_invoice(self):
        if self.against_invoice:
            frappe.db.set_value("Sales Invoice", self.against_invoice, "outstanding_amount",
                frappe.db.get_value("Sales Invoice", self.against_invoice, "outstanding_amount") - self.grand_total)

    def revert_original_invoice(self):
        if self.against_invoice:
            frappe.db.set_value("Sales Invoice", self.against_invoice, "outstanding_amount",
                frappe.db.get_value("Sales Invoice", self.against_invoice, "outstanding_amount") + self.grand_total)

    def reverse_commission(self):
        if not self.against_invoice:
            return
        # Find the expense account from original invoice's commission applied terms
        expense_account = None
        orig_terms = frappe.get_doc("Sales Invoice", self.against_invoice).get("applied_commercial_terms")
        for t in orig_terms:
            if t.effect == "Commission" and t.account:
                expense_account = t.account
                break
        
        entries = frappe.db.sql('''
            SELECT agent, commission_amount
            FROM `tabCommission Ledger`
            WHERE invoice = %s AND status = 'Accrued'
        ''', self.against_invoice, as_dict=True)
        for e in entries:
            rev = frappe.get_doc({
                "doctype": "Commission Ledger",
                "agent": e.agent,
                "invoice": self.against_invoice,
                "commission_amount": -abs(flt(e.commission_amount)),
                "status": "Recovered",
                "posting_date": self.posting_date,
                "remarks": "Reversed by Credit Note " + self.name,
            })
            rev.flags.ignore_permissions = True
            rev.insert()
            agent_account = frappe.db.get_value("Sales Agent", e.agent, "default_commission_account")
            if expense_account and agent_account:
                # Dr Commission Payable (reverse original Cr)
                gl1 = frappe.get_doc({
                    "doctype": "GL Entry",
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "account": agent_account,
                    "debit": abs(flt(e.commission_amount)),
                    "credit": 0,
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "party_type": "Sales Agent",
                    "party": e.agent,
                })
                gl1.flags.ignore_permissions = True
                gl1.insert()
                # Cr Commission Expense (reverse original Dr)
                gl2 = frappe.get_doc({
                    "doctype": "GL Entry",
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "account": expense_account,
                    "debit": 0,
                    "credit": abs(flt(e.commission_amount)),
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                })
                gl2.flags.ignore_permissions = True
                gl2.insert()
    def undo_reverse_commission(self):
        rev_ledgers = frappe.get_all("Commission Ledger", filters={
            "remarks": ("like", "Reversed by Credit Note " + self.name),
        })
        for r in rev_ledgers:
            frappe.db.set_value("Commission Ledger", r.name, "status", "Cancelled")
