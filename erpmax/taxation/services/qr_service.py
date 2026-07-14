import frappe, base64
from ..providers import get_provider_for_country


class QRService:

    def _get_invoice_tax_total(self, si):
        return si.get('tax_total') or si.get('total_tax') or 0

    def generate_qr(self, ci_name):
        ci = frappe.get_doc('Tax Compliance Invoice', ci_name)
        profile = frappe.get_doc('Tax Country Profile', ci.provider)
        provider = get_provider_for_country(profile.country_code)

        si = frappe.get_doc('Sales Invoice', ci.erpnext_invoice)
        company = frappe.get_doc('Company', si.company)

        data = {
            'seller': {'name': company.company_name, 'vat_number': company.get('vat_number', '')},
            'issue_date': si.posting_date,
            'issue_time': '',
            'grand_total': si.grand_total or 0,
            'total_vat': self._get_invoice_tax_total(si),
        }

        qr_b64 = provider.generate_qr(data)
        if not qr_b64:
            return ci

        file_doc = frappe.get_doc({
            'doctype': 'File',
            'file_name': 'QR_{}.png'.format(ci.name),
            'content': base64.b64decode(qr_b64),
            'attached_to_doctype': 'Tax Compliance Invoice',
            'attached_to_name': ci.name,
            'is_private': 0,
        })
        file_doc.insert(ignore_permissions=True)
        ci.qr_code = file_doc.file_url
        ci.save()
        return ci
