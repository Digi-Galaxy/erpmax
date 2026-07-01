import frappe
from ..providers import get_provider_for_country


class SigningService:

    def sign_einvoice(self, einvoice_name):
        einvoice = frappe.get_doc("EH E-Invoice", einvoice_name)
        provider_config = frappe.get_doc("EH Provider Config", einvoice.provider_config)
        profile = frappe.get_doc("EH Country Profile", einvoice.country_profile)

        provider = get_provider_for_country(profile.country_code)

        if einvoice.signed_xml:
            return einvoice

        cert = None
        if provider_config.signing_certificate:
            cert_doc = frappe.get_doc("EH Signing Certificate", provider_config.signing_certificate)
            if cert_doc.certificate:
                cert = frappe.get_doc("File", {"file_url": cert_doc.certificate}).get_content()
            private_key_content = None
            if cert_doc.private_key:
                private_key_content = frappe.get_doc("File", {"file_url": cert_doc.private_key}).get_content()
        else:
            frappe.throw("No signing certificate configured in Provider Config")

        signed_xml = provider.sign_invoice(einvoice.xml_content, cert, private_key_content)
        einvoice.signed_xml = signed_xml

        log = self._create_submission_log(einvoice, "Sign", "Success")

        einvoice.status = "Signed"
        einvoice.save()
        return einvoice

    def _create_submission_log(self, einvoice, action, status, error=None):
        log = frappe.get_doc({
            "doctype": "EH Submission Log",
            "einvoice": einvoice.name,
            "action_type": action,
            "status": status,
            "timestamp": frappe.utils.now_datetime(),
            "error_message": error or "",
        })
        log.insert()
        return log
