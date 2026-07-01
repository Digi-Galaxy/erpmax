import frappe
from frappe.model.document import Document

class Company(Document):
    @frappe.whitelist()
    def create_chart_of_accounts(self):
        from erpmax.accounts.create_charts import build_account_tree

        if not self.chart_template:
            frappe.throw("Select a Chart Template first")

        try:
            accounts = build_account_tree(self.name, self.chart_template)
            frappe.msgprint(f"Created {len(accounts)} accounts from {self.chart_template}")
        except Exception as e:
            frappe.log_error(f"COA creation failed: {str(e)}", "Chart of Accounts")
            frappe.throw(f"Failed to create accounts: {str(e)}")

        return accounts
