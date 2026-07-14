import frappe
from frappe.model.document import Document


class Customer(Document):
    def validate(self):
        self.set_abbr()
        self.set_default_accounts()

    def after_insert(self):
        """Auto-create account when customer is created"""
        self.create_customer_account()

    def set_abbr(self):
        if not self.customer_abbr and self.customer_name:
            from erpmax.utils.naming import make_abbreviation
            self.customer_abbr = make_abbreviation(self.customer_name, fallback="CUST")

    def set_default_accounts(self):
        if not self.default_receivable_account:
            self.default_receivable_account = self._get_default_receivable_account()

        if not self.default_income_account:
            self.default_income_account = self._get_default_income_account()

    def create_customer_account(self):
        """Auto-create receivable account for customer"""
        # Check if auto-create is enabled
        try:
            party_type_doc = frappe.get_doc("Party Type", "Customer")
            if not party_type_doc.auto_create_account:
                return
        except:
            # If Party Type doesn't exist, use default behavior
            pass

        # Get company
        company = self.company or frappe.defaults.get_default("company")
        if not company:
            return

        # Create account name
        account_name = f"CUST-{self.customer_name}"

        # Check if account already exists
        existing = frappe.db.get_value("Account", {
            "account_name": account_name,
            "company": company
        })

        if existing:
            self.default_receivable_account = existing
            return

        # Get parent account
        parent_account = self._get_default_receivable_account()
        if not parent_account:
            frappe.msgprint(_("No receivable account found. Please create one first."))
            return

        # Create account
        try:
            account = frappe.get_doc({
                "doctype": "Account",
                "account_name": account_name,
                "account_type": "Receivable",
                "root_type": "Asset",
                "company": company,
                "parent_account": parent_account,
                "is_group": 0
            })
            account.insert(ignore_permissions=True)
            frappe.db.commit()

            self.default_receivable_account = account.name
            frappe.msgprint(_("Account {0} created automatically").format(account_name))
        except Exception as e:
            frappe.log_error(f"Failed to create account for customer {self.customer_name}: {str(e)}")

    def _get_default_receivable_account(self):
        if self.company:
            account = frappe.db.get_value("Account", {
                "company": self.company,
                "account_type": "Receivable",
                "is_group": 0
            }, "name")
            if account:
                return account

        account = frappe.db.get_value("Account", {
            "account_type": "Receivable",
            "is_group": 0
        }, "name")
        return account

    def _get_default_income_account(self):
        if self.company:
            account = frappe.db.get_value("Account", {
                "company": self.company,
                "account_type": "Income",
                "is_group": 0
            }, "name")
            if account:
                return account

        account = frappe.db.get_value("Account", {
            "account_type": "Income",
            "is_group": 0
        }, "name")
        return account
