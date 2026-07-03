from frappe.utils.nestedset import NestedSet


class ItemCategory(NestedSet):
    nsm_parent_field = "parent_item_category"
