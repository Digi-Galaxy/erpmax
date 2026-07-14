import frappe
from frappe.model.document import Document


def _make_account_name(partner_name: str, suffix: str) -> str:
    return f"{(partner_name or '').strip()} {suffix}".strip()


class PartnerAccount(Document):
    def after_insert(self):
        if self.create_default_accounts:
            self.ensure_default_accounts()

    def ensure_default_accounts(self):
        self.receivable_account = self.receivable_account or self._ensure_account(
            _make_account_name(self.partner_name, "Receivable"), "Asset"
        )
        self.payable_account = self.payable_account or self._ensure_account(
            _make_account_name(self.partner_name, "Payable"), "Liability"
        )
        self.capital_account = self.capital_account or self._ensure_account(
            _make_account_name(self.partner_name, "Capital"), "Equity"
        )
        self.retention_account = self.retention_account or self._ensure_account(
            _make_account_name(self.partner_name, "Retention"), "Liability"
        )
        self.db_set(
            {
                "receivable_account": self.receivable_account,
                "payable_account": self.payable_account,
                "capital_account": self.capital_account,
                "retention_account": self.retention_account,
            }
        )

    def _ensure_account(self, account_name, root_type):
        existing = frappe.db.get_value(
            "Account", {"account_name": account_name, "company": self.company}, "name"
        )
        if existing:
            return existing

        account = frappe.get_doc(
            {
                "doctype": "Account",
                "account_name": account_name,
                "company": self.company,
                "root_type": root_type,
                "report_type": "Balance Sheet",
                "is_group": 0,
            }
        )
        account.flags.ignore_permissions = True
        account.insert()
        return account.name
