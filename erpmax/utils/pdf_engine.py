import frappe
from frappe.utils.file_manager import save_file
from erpmax.utils.chrome_pdf import get_pdf as chrome_get_pdf


def generate_pdf(doctype, name, print_format=None):
    doc = frappe.get_doc(doctype, name)
    html = frappe.get_print(doctype, name, print_format=print_format, no_letterhead=0)
    return chrome_get_pdf(html, options={"page-size": "A4"})


def save_pdf(pdf_bytes, doctype, name, folder="Home/Attachments", public=False):
    fname = f"{doctype}-{name}.pdf".replace(" ", "-").replace("/", "-")
    file_doc = save_file(
        fname=fname, content=pdf_bytes, dt=doctype, dn=name,
        folder=folder, is_private=0 if public else 1,
    )
    return (file_doc.file_url, file_doc.file_name, file_doc.name)

