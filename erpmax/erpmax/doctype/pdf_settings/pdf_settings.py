import frappe
from frappe.model.document import Document

class PDFSettings(Document):
    def validate(self):
        if self.use_chrome_pdf:
            self._check_chrome()

    def _check_chrome(self):
        import shutil
        chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
        if not chrome:
            frappe.msgprint(
                "Google Chrome not found on server. Chrome PDF engine will not work. "
                "Install chrome or disable Use Chrome PDF Engine.",
                alert=True,
                indicator="orange",
            )
