import frappe
from frappe import _
from frappe.model.document import Document


class CommissionPayment(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        self.payment_amount = sum((row.allocated_amount or 0) for row in self.entries)
    
    def on_submit(self):
        self.status = "Paid"
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
        
        for row in self.entries:
            gl = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": payable_account,
                "debit": row.allocated_amount,
                "credit": 0,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": "Sales Agent",
                "party": self.agent,
            })
            gl.flags.ignore_permissions = True
            gl.insert()
            
            gl2 = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": self.payment_account,
                "debit": 0,
                "credit": row.allocated_amount,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
            })
            gl2.flags.ignore_permissions = True
            gl2.insert()
    
    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)
    
    def update_ledger_entries(self):
        for row in self.entries:
            ledger = frappe.get_doc("Commission Ledger", row.commission_ledger)
            ledger.db_set("status", "Paid")
            ledger.db_set("paid_date", self.posting_date)
            ledger.db_set("payment_reference", self.name)
    
    def revert_ledger_entries(self):
        for row in self.entries:
            ledger = frappe.get_doc("Commission Ledger", row.commission_ledger)
            ledger.db_set("status", "Accrued")
            ledger.db_set("paid_date", None)
            ledger.db_set("payment_reference", None)
