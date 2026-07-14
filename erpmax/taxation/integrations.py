import frappe
from .services.invoice_service import InvoiceService
from .services.signing_service import SigningService
from .services.qr_service import QRService
from .services.queue_service import QueueService


def on_sales_invoice_submit(doc, method):
    settings = frappe.get_single('Tax Compliance Settings')
    if not settings.enabled or not settings.auto_generate:
        return

    profile = frappe.db.get_value('Tax Country Profile',
        {'country': frappe.db.get_value('Company', doc.company, 'country'), 'enabled': 1},
        'name')
    if not profile:
        return

    try:
        svc = InvoiceService()
        ci = svc.create_compliance_invoice(doc.name)
        if ci.status == 'Failed':
            frappe.msgprint('Tax compliance validation failed: {}'.format(ci.validation_results))
            return

        signing_svc = SigningService()
        ci = signing_svc.sign_compliance_invoice(ci.name)

        qr_svc = QRService()
        qr_svc.generate_qr(ci.name)

        if settings.auto_submit:
            qs = QueueService()
            qs.enqueue(ci.name)

    except Exception as e:
        frappe.log_error('Tax Compliance auto-generation error for {}: {}'.format(doc.name, str(e)), 'Tax Compliance')


def on_sales_invoice_cancel(doc, method):
    settings = frappe.get_single("Tax Compliance Settings")
    if not settings.enabled:
        return

    ci = frappe.db.get_value("Tax Compliance Invoice",
        {"erpnext_invoice": doc.name, "status": "Submitted"},
        ["name", "provider"], as_dict=True)
    if ci:
        frappe.throw(
            "Cannot cancel Sales Invoice {}: already submitted to tax authority ({})".format(
                doc.name, ci.provider)
        )
