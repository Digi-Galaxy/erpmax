import frappe
from frappe.model.document import Document

from erpmax.erpmax_geo.registry import clear_geo_caches


class GeoSettings(Document):
    def validate(self):
        for fieldname in (
            "default_radius_m",
            "autocomplete_bias_radius_m",
        ):
            value = self.get(fieldname)
            if value in (None, ""):
                continue
            try:
                self.set(fieldname, max(0, int(value)))
            except Exception:
                self.set(fieldname, 0)

    def on_update(self):
        clear_geo_caches()
