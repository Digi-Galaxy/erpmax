import frappe
import base64
from ..providers import get_provider_for_country


class QRService:

    def generate_qr_for_einvoice(self, einvoice_name):
        einvoice = frappe.get_doc("EH E-Invoice", einvoice_name)
        profile = frappe.get_doc("EH Country Profile", einvoice.country_profile)
        provider_config = frappe.get_doc("EH Provider Config", einvoice.provider_config)

        provider = get_provider_for_country(profile.country_code)

        si = frappe.get_doc("Sales Invoice", einvoice.erpnext_invoice)
        company = frappe.get_doc("Company", si.company)

        invoice_data = {
            "seller": {
                "name": company.company_name,
                "vat_number": company.vat_number,
            },
            "issue_date": si.posting_date,
            "issue_time": "",
            "grand_total": si.grand_total or 0,
            "total_vat": si.total_tax or 0,
        }

        qr_base64 = provider.generate_qr(invoice_data)

        from frappe.utils.file_manager import save_file
        filename = "QR_{0}.png".format(einvoice.name)
        file_data = base64.b64decode(qr_base64)
        file_doc = save_file(
            filename,
            file_data,
            "EH E-Invoice",
            einvoice.name,
            is_private=0,
        )

        einvoice.qr_code = file_doc.file_url
        einvoice.save()
        return einvoice
