import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class ItemCategory(NestedSet):
    nsm_parent_field = "parent_item_category"


@frappe.whitelist()
def get_children(parent=None, company=None, **kwargs):
	root = parent or company or ""
	filters = {"parent_item_category": root}
	if company:
		filters["company"] = company
	categories = frappe.get_all(
		"Item Category",
		filters=filters,
		fields=["name", "category_name", "is_group", "company"],
		order_by="category_name asc",
	)
	return [
		{
			"value": row.name,
			"title": row.category_name or row.name,
			"expandable": 1 if row.is_group else 0,
			"company": row.company,
		}
		for row in categories
	]


@frappe.whitelist()
def add_node(parent=None, label=None, company=None, **kwargs):
	label = (label or "").strip()
	if not label:
		frappe.throw(_("Category Name is required"))
	if not company:
		frappe.throw(_("Company is required"))

	doc = frappe.get_doc(
		{
			"doctype": "Item Category",
			"category_name": label,
			"company": company,
			"parent_item_category": parent or None,
			"is_group": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.as_dict()
