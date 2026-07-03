import frappe
from frappe.tests.utils import FrappeTestCase


class TestAccount(FrappeTestCase):
    def test_tree_structure(self):
        accounts = frappe.get_all("Account", fields=["name", "parent_account", "lft", "rgt", "is_group"])
        self.assertGreaterEqual(len(accounts), 3)

        for a in accounts:
            self.assertIsNotNone(a.lft)
            self.assertIsNotNone(a.rgt)
            self.assertLess(a.lft, a.rgt)
            if a.parent_account:
                parent = frappe.get_doc("Account", a.parent_account)
                self.assertGreater(a.lft, parent.lft)
                self.assertLess(a.rgt, parent.rgt)

    def test_parent_company_validation(self):
        company = frappe.get_all("Company", fields=["name"], limit=1)
        if not company:
            return
        company_name = company[0].name

        parent = frappe.get_doc(
            {
                "doctype": "Account",
                "account_name": "Test Parent Co",
                "company": company_name,
                "root_type": "Asset",
                "is_group": 1,
            }
        )
        parent.insert()

        child = frappe.get_doc(
            {
                "doctype": "Account",
                "account_name": "Test Child Co",
                "company": company_name,
                "root_type": "Asset",
                "parent_account": parent.name,
                "is_group": 0,
            }
        )
        child.insert()
        self.assertEqual(child.parent_account, parent.name)

        frappe.delete_doc("Account", child.name)
        frappe.delete_doc("Account", parent.name)

    def test_group_freezes_account(self):
        acc = frappe.get_doc(
            {
                "doctype": "Account",
                "account_name": "Freeze Test",
                "company": frappe.get_all("Company", fields=["name"], limit=1)[0].name,
                "root_type": "Asset",
                "is_group": 1,
                "freeze_account": 1,
            }
        )
        acc.insert()
        self.assertEqual(acc.freeze_account, 0)
        frappe.delete_doc("Account", acc.name)
