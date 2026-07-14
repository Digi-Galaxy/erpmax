import frappe
from frappe import _
from frappe.utils.file_manager import save_file
from erpmax.utils.pdf_generator import generate_pdf


def generate_contract_pdf(doctype, docname, print_format=None):
    """Generate and save PDF for a contract document (TMS-style)."""
    doc = frappe.get_doc(doctype, docname)

    if not print_format:
        print_format = frappe.db.get_value(
            "Print Format",
            {"doc_type": doctype, "is_default": 1},
            "name"
        )

    try:
        html = frappe.get_print(
            doctype,
            docname,
            print_format=print_format,
            no_letterhead=0,
        )

        pdf_bytes = generate_pdf(html, pdf_generator="chrome")
    except Exception as e:
        frappe.log_error(f"PDF generation failed for {doctype} {docname}: {str(e)}")
        frappe.throw(_("Failed to generate PDF: {0}").format(str(e)))

    customer_name = doc.get("customer_name") or doc.get("customer") or "Unknown"
    fname = f"{doctype}-{docname}.pdf".replace(" ", "-").replace("/", "-")

    folder_path = _ensure_customer_folder(customer_name)

    file_doc = save_file(
        fname=fname,
        content=pdf_bytes,
        dt=doctype,
        dn=docname,
        folder=folder_path,
        is_private=1,
    )

    return {
        "file_url": file_doc.file_url,
        "file_name": fname,
        "folder": f"Home / Customers / {customer_name}",
    }


def _ensure_customer_folder(customer_name):
    """Ensure the folder structure: Home/Customers/<customer_name>/ exists."""
    home = frappe.get_doc("File", {"file_name": "Home", "is_folder": 1})
    customers_folder = _ensure_subfolder("Customers", home.name)
    customer_folder = _ensure_subfolder(customer_name, customers_folder)
    return customer_folder


def _ensure_subfolder(folder_name, parent_folder):
    existing = frappe.db.get_value(
        "File",
        {"file_name": folder_name, "folder": parent_folder, "is_folder": 1},
    )
    if existing:
        return existing
    folder = frappe.get_doc({
        "doctype": "File",
        "file_name": folder_name,
        "is_folder": 1,
        "folder": parent_folder,
    })
    folder.insert(ignore_permissions=True)
    return folder.name
