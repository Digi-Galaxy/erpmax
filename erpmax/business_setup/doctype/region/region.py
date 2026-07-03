from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


class Region(NestedSet):
    nsm_parent_field = "parent_region"
