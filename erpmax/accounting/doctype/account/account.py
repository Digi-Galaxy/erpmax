import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class Account(NestedSet):
    nsm_parent_field = "parent_account"

    def validate(self):
        if self.is_group:
            self.freeze_account = 0
        self.validate_parent_company()

    def validate_parent_company(self):
        if self.parent_account:
            parent = frappe.get_cached_doc("Account", self.parent_account)
            if parent.company != self.company:
                frappe.throw(
                    _("Parent account {0} belongs to company {1}, but this account company is {2}").format(
                        parent.account_name, parent.company, self.company
                    )
                )


@frappe.whitelist()
def get_children(parent=None, company=None, **kwargs):
    root = parent or ""
    filters = {"parent_account": root}
    if company:
        filters["company"] = company
    accounts = frappe.get_all(
        "Account",
        filters=filters,
        fields=["name", "account_name", "is_group", "company", "root_type"],
        order_by="account_name asc",
    )
    return [
        {
            "value": row.name,
            "title": row.account_name,
            "expandable": 1 if row.is_group else 0,
            "company": row.company,
        }
        for row in accounts
    ]


@frappe.whitelist()
def add_node(parent=None, label=None, company=None, root_type=None, **kwargs):
    label = (label or "").strip()
    if not label:
        frappe.throw(_("Account Name is required"))
    if not company:
        frappe.throw(_("Company is required"))
    if not root_type:
        frappe.throw(_("Root Type is required"))

    doc = frappe.get_doc(
        {
            "doctype": "Account",
            "account_name": label,
            "company": company,
            "root_type": root_type,
            "parent_account": parent or None,
            "is_group": 1,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.as_dict()
