import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class CommissionRecovery(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        total = sum(flt(row.recovered_amount) for row in self.entries)
        self.recovery_amount = total
    
    def on_submit(self):
        self.status = "Recovered"
        self.make_gl_entries()
        self.update_ledger_entries()
    
    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()
        self.revert_ledger_entries()
    
    def make_gl_entries(self):
        agent = frappe.get_cached_doc("Sales Agent", self.agent)
        payable_account = agent.default_commission_account
        if not payable_account:
            frappe.throw(_("Agent {0} has no default commission account").format(self.agent))
        expense_account = None
        for row in self.entries:
            ledger = frappe.get_doc("Commission Ledger", row.commission_ledger)
            exp_ac = frappe.db.get_value("Applied Commercial Terms", 
                {"parent": ledger.invoice, "effect": "Commission", "party": self.agent}, "account")
            if exp_ac:
                expense_account = exp_ac
                break
        if not expense_account:
            expense_account = frappe.db.get_value("Account", 
                {"account_name": "Commission Expense", "company": self.company}, "name")
        for row in self.entries:
            gl1 = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": payable_account,
                "debit": flt(row.recovered_amount),
                "credit": 0,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": "Sales Agent",
                "party": self.agent,
            })
            gl1.flags.ignore_permissions = True
            gl1.insert()
            gl2 = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": expense_account,
                "debit": 0,
                "credit": flt(row.recovered_amount),
                "voucher_type": self.doctype,
                "voucher_no": self.name,
            })
            gl2.flags.ignore_permissions = True
            gl2.insert()
    
    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={"voucher_type": self.doctype, "voucher_no": self.name})
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)
    
    def update_ledger_entries(self):
        for row in self.entries:
            ledger = frappe.get_doc("Commission Ledger", row.commission_ledger)
            reverse_ledger = frappe.get_doc({
                "doctype": "Commission Ledger",
                "agent": self.agent,
                "invoice": ledger.invoice,
                "commission_amount": -abs(flt(row.recovered_amount)),
                "status": "Recovered",
                "posting_date": self.posting_date,
                "remarks": "Recovered by " + self.name,
            })
            reverse_ledger.flags.ignore_permissions = True
            reverse_ledger.insert()
    
    def revert_ledger_entries(self):
        rev_entries = frappe.get_all("Commission Ledger", filters={
            "remarks": ("like", "Recovered by " + self.name),
        })
        for r in rev_entries:
            frappe.db.set_value("Commission Ledger", r.name, "status", "Cancelled")
