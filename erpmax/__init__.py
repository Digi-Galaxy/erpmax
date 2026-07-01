from frappe.utils import pdf as frappe_pdf
import erpmax.utils.chrome_pdf as chrome_pdf

def get_pdf(html, options=None, output=None):
    try:
        return chrome_pdf.get_pdf(html, options=options, output=output)
    except Exception:
        return frappe_pdf.get_pdf(html, options=options, output=output)

