import frappe
from .services.invoice_service import InvoiceService
from .services.signing_service import SigningService
from .services.submission_service import SubmissionService
from .services.qr_service import QRService


def on_sales_invoice_submit(doc, method):
    settings = frappe.get_single("EH Settings")
    if not settings.auto_generate_einvoice:
        return

    company = frappe.get_doc("Company", doc.company)
    if not company.enable_zatca_e_invoicing:
        return

    einvoice = InvoiceService().create_einvoice_from_sales_invoice(doc.name)

    if settings.auto_sign_invoice and einvoice.status == "Validated":
        einvoice = SigningService().sign_einvoice(einvoice.name)

    if settings.auto_submit_invoice and einvoice.status == "Signed":
        einvoice = SubmissionService().submit_einvoice(einvoice.name)
        QRService().generate_qr_for_einvoice(einvoice.name)
