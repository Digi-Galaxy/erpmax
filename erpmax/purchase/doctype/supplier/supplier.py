import frappe
from frappe.model.document import Document


class Supplier(Document):
    def validate(self):
        self.set_abbr()
        self.set_default_accounts()

    def after_insert(self):
        """Auto-create account when supplier is created"""
        self.create_supplier_account()

    def set_abbr(self):
        if not self.supplier_abbr and self.supplier_name:
            from erpmax.utils.naming import make_abbreviation
            self.supplier_abbr = make_abbreviation(self.supplier_name, fallback="SUP")

    def set_default_accounts(self):
        if not self.default_payable_account:
            self.default_payable_account = self._get_default_payable_account()

        if not self.default_expense_account:
            self.default_expense_account = self._get_default_expense_account()

    def create_supplier_account(self):
        """Auto-create payable account for supplier"""
        # Check if auto-create is enabled
        try:
            party_type_doc = frappe.get_doc("Party Type", "Supplier")
            if not party_type_doc.auto_create_account:
                return
        except:
            pass

        # Get company
        company = self.company or frappe.defaults.get_default("company")
        if not company:
            return

        # Create account name
        account_name = f"SUPP-{self.supplier_name}"

        # Check if account already exists
        existing = frappe.db.get_value("Account", {
            "account_name": account_name,
            "company": company
        })

        if existing:
            self.default_payable_account = existing
            return

        # Get parent account
        parent_account = self._get_default_payable_account()
        if not parent_account:
            frappe.msgprint(_("No payable account found. Please create one first."))
            return

        # Create account
        try:
            account = frappe.get_doc({
                "doctype": "Account",
                "account_name": account_name,
                "account_type": "Payable",
                "root_type": "Liability",
                "company": company,
                "parent_account": parent_account,
                "is_group": 0
            })
            account.insert(ignore_permissions=True)
            frappe.db.commit()

            self.default_payable_account = account.name
            frappe.msgprint(_("Account {0} created automatically").format(account_name))
        except Exception as e:
            frappe.log_error(f"Failed to create account for supplier {self.supplier_name}: {str(e)}")

    def _get_default_payable_account(self):
        if self.company:
            account = frappe.db.get_value("Account", {
                "company": self.company,
                "account_type": "Payable",
                "is_group": 0
            }, "name")
            if account:
                return account

        account = frappe.db.get_value("Account", {
            "account_type": "Payable",
            "is_group": 0
        }, "name")
        return account

    def _get_default_expense_account(self):
        if self.company:
            account = frappe.db.get_value("Account", {
                "company": self.company,
                "account_type": "Expense",
                "is_group": 0
            }, "name")
            if account:
                return account

        account = frappe.db.get_value("Account", {
            "account_type": "Expense",
            "is_group": 0
        }, "name")
        return account
