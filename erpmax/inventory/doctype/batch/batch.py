import frappe
from frappe.model.document import Document

class Batch(Document):
    def validate(self):
        if self.item:
            item = frappe.get_cached_doc("Item", self.item)
            if not item.has_batch_no:
                frappe.throw("Item {} does not have batch tracking enabled".format(self.item))
        self.set_expiry_date()

    def set_expiry_date(self):
        if self.manufacturing_date and self.expiry_date:
            return
        if self.manufacturing_date and self.item:
            item = frappe.get_cached_doc("Item", self.item)
            if item.has_expiry_date and item.shelf_life_in_days:
                from datetime import timedelta
                dt = self.manufacturing_date
                if isinstance(dt, str):
                    from datetime import datetime
                    dt = datetime.strptime(dt, "%Y-%m-%d").date()
                self.expiry_date = dt + timedelta(days=item.shelf_life_in_days)
