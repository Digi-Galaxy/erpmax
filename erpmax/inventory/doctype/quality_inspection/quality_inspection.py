import frappe
from frappe.model.document import Document

class QualityInspection(Document):
    def validate(self):
        self.set_status()
        self.update_child_status()

    def set_status(self):
        if not self.readings:
            return
        all_accepted = all(r.status == "Accepted" for r in self.readings)
        self.status = "Accepted" if all_accepted else "Rejected"

    def update_child_status(self):
        for r in self.readings:
            if r.numeric and r.min_value is not None and r.max_value is not None:
                values = []
                for i in range(1, 11):
                    v = getattr(r, "reading_{}".format(i), None)
                    if v is not None:
                        values.append(v)
                if values:
                    avg = sum(values) / len(values)
                    r.status = "Accepted" if r.min_value <= avg <= r.max_value else "Rejected"
