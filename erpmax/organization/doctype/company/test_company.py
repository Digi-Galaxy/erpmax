import frappe
from frappe.tests.utils import FrappeTestCase


class TestCompany(FrappeTestCase):
    def test_tree_structure(self):
        companies = frappe.get_all("Company", fields=["name", "parent_company", "lft", "rgt", "is_group"])
        self.assertGreaterEqual(len(companies), 4)

        root = frappe.get_doc("Company", "Root Holding")
        self.assertTrue(root.is_group)
        self.assertIsNone(root.parent_company)

        for c in companies:
            self.assertIsNotNone(c.lft)
            self.assertIsNotNone(c.rgt)
            self.assertLess(c.lft, c.rgt)
            if c.parent_company:
                parent = frappe.get_doc("Company", c.parent_company)
                self.assertGreater(c.lft, parent.lft)
                self.assertLess(c.rgt, parent.rgt)

    def test_abbreviation_auto_generated(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": "Alpha Beta Gamma",
                "status": "Draft",
                "company_type": "LLC",
                "business_type": "Services",
                "country": "Saudi Arabia",
                "address_line_1": "Test Street",
                "city": "Riyadh",
            }
        )
        company.insert()
        self.assertEqual(company.abbreviation, "ABG")
        frappe.delete_doc("Company", company.name)

    def test_status_defaults_to_draft(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": "Status Test Co",
                "company_type": "LLC",
                "business_type": "Services",
                "country": "Saudi Arabia",
                "address_line_1": "Test Street",
                "city": "Riyadh",
            }
        )
        company.insert()
        self.assertEqual(company.status, "Draft")
        frappe.delete_doc("Company", company.name)
