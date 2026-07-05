import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class BankTransaction(Document):
    def validate(self):
        self.calculate_balance()

    def calculate_balance(self):
        if self.status == "Reconciled" and self.payment_entry:
            self.balance = 0
        else:
            self.balance = self.amount

    def on_update(self):
        self.update_bank_balance()

    def update_bank_balance(self):
        if self.bank_account:
            balance = frappe.db.get_value("Bank Transaction", {
                "bank_account": self.bank_account,
                "status": ["!=", "Cancelled"],
            }, "sum(amount)") or 0
            frappe.db.set_value("Bank Account", self.bank_account, "current_balance", balance)

    @frappe.whitelist()
    def reconcile(self, payment_entry=None, journal_entry=None):
        if payment_entry:
            self.payment_entry = payment_entry
            self.voucher_type = "Payment Entry"
            self.voucher_no = payment_entry
        elif journal_entry:
            self.journal_entry = journal_entry
            self.voucher_type = "Journal Entry"
            self.voucher_no = journal_entry
        else:
            frappe.throw("Please select a Payment Entry or Journal Entry to reconcile")

        self.status = "Reconciled"
        self.reconciled_date = nowdate()
        self.save()

        return {"status": "Reconciled", "voucher": self.voucher_no}

    @frappe.whitelist()
    def unreconcile(self):
        self.payment_entry = None
        self.journal_entry = None
        self.voucher_type = None
        self.voucher_no = None
        self.status = "Pending"
        self.reconciled_date = None
        self.save()

        return {"status": "Pending"}

    @frappe.whitelist()
    def create_payment_entry(self):
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive" if self.transaction_type == "Credit" else "Pay",
            "party_type": "Customer" if self.transaction_type == "Credit" else "Supplier",
            "posting_date": self.posting_date,
            "company": self.company,
            "paid_amount": self.amount,
            "received_amount": self.amount,
            "paid_from": self.bank_account_link,
            "paid_to": self.bank_account_link,
            "reference_doctype": "Bank Transaction",
            "reference_name": self.name,
        })
        pe.insert()
        self.reconcile(payment_entry=pe.name)
        return pe.name

    @frappe.whitelist()
    def create_journal_entry(self):
        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "posting_date": self.posting_date,
            "company": self.company,
            "accounts": [{
                "account": self.bank_account_link,
                "debit": self.amount if self.transaction_type == "Debit" else 0,
                "credit": 0 if self.transaction_type == "Debit" else self.amount,
            }, {
                "account": self.default_expense_account or self.bank_account_link,
                "debit": 0 if self.transaction_type == "Debit" else self.amount,
                "credit": self.amount if self.transaction_type == "Debit" else 0,
            }],
        })
        je.insert()
        self.reconcile(journal_entry=je.name)
        return je.name
