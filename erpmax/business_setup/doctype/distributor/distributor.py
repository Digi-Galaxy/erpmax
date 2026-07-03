from frappe.utils.nestedset import NestedSet


class Distributor(NestedSet):
    nsm_parent_field = "parent_distributor"
