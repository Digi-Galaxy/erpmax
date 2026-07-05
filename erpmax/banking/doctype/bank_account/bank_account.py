import frappe
from frappe.model.document import Document


class BankAccount(Document):
    def validate(self):
        self.validate_account()
        self.set_abbr()

    def validate_account(self):
        if self.account:
            account = frappe.get_doc("Account", self.account)
            if account.company and account.company != self.company:
                frappe.throw("Account must belong to the same company")

    def set_abbr(self):
        if not self.bank_account_abbr and self.bank_account_name:
            from erpmax.utils.naming import make_abbreviation
            self.bank_account_abbr = make_abbreviation(self.bank_account_name, fallback="BANK")

    def get_balance(self):
        balance = frappe.db.get_value("GL Entry", {
            "account": self.account,
            "company": self.company,
            "is_cancelled": 0,
        }, ["sum(debit)", "sum(credit)"])
        debit = balance[0] or 0
        credit = balance[1] or 0
        return debit - credit

    def get_last_sync_date(self):
        last = frappe.db.get_value("Bank Statement", {
            "bank_account": self.name,
            "docstatus": 1,
        }, "posting_date", order_by="posting_date desc")
        return last

    @frappe.whitelist()
    def sync_from_bank(self):
        """Sync transactions from connected bank"""
        connection = frappe.db.get_value("Bank Connection", {
            "bank_account": self.name,
            "status": "Connected",
        }, "name")
        if connection:
            conn = frappe.get_doc("Bank Connection", connection)
            return conn.sync_transactions()
        return {"error": "No active bank connection"}
