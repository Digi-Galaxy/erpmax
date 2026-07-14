import frappe
from frappe.model.document import Document

class SerialNo(Document):
    def validate(self):
        if self.item_code:
            item = frappe.get_cached_doc("Item", self.item_code)
            if not item.has_serial_no:
                frappe.throw("Item {} does not have serial number tracking enabled".format(self.item_code))
