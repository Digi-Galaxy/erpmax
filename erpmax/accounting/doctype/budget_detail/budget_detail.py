# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class BudgetDetail(Document):
    def validate(self):
        self.set_account_name()
    
    def set_account_name(self):
        """Set account name from account"""
        if self.account:
            self.account_name = frappe.db.get_value("Account", self.account, "account_name")
