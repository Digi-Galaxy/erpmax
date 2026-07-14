import frappe
from ..providers import get_provider_for_country


class SigningService:

    def sign_compliance_invoice(self, ci_name):
        ci = frappe.get_doc('Tax Compliance Invoice', ci_name)
        profile = frappe.get_doc('Tax Country Profile', ci.provider)
        provider = get_provider_for_country(profile.country_code)

        if ci.signed_xml:
            return ci

        cert_content = None
        private_key_content = None
        provider_config = frappe.db.get_value('Tax Provider Config',
            {'company': ci.company}, '*')
        if provider_config and provider_config.get('signing_certificate'):
            cert_doc = frappe.get_doc('Tax Signing Certificate', provider_config['signing_certificate'])
            if cert_doc.certificate:
                file = frappe.get_doc('File', {'file_url': cert_doc.certificate})
                cert_content = file.get_content()
            if cert_doc.private_key:
                file = frappe.get_doc('File', {'file_url': cert_doc.private_key})
                private_key_content = file.get_content()

        signed = provider.sign_invoice(ci.xml_content, cert_content, private_key_content)
        ci.signed_xml = signed
        ci.status = 'Signed'
        ci.save()
        return ci
