import frappe
from ..base_provider import BaseProvider
from .xml_builder import ZATCAXMLBuilder
from .signer import ZATCASigner
from .qr_generator import ZATCAQRGenerator
from .validator import ZATCAValidator


class ZATCAProvider(BaseProvider):

    def __init__(self):
        self.xml_builder = ZATCAXMLBuilder()
        self.signer = ZATCASigner()
        self.qr_generator = ZATCAQRGenerator()
        self.validator = ZATCAValidator()

    def get_api_base_url(self, provider_config):
        profile = frappe.get_doc("EH Country Profile", provider_config.country_profile)
        env = provider_config.environment or "Sandbox"
        if env == "Production":
            return profile.api_base_url_production or "https://gw-fatoora.zatca.gov.sa/e-invoicing"
        return profile.api_base_url_sandbox or "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer"

    def generate_xml(self, invoice_data):
        return self.xml_builder.build(invoice_data)

    def sign_invoice(self, xml_content, certificate, private_key):
        return self.signer.sign(xml_content, certificate, private_key)

    def generate_qr(self, invoice_data, signed_xml=None):
        return self.qr_generator.generate(invoice_data)

    def validate(self, invoice_data):
        return self.validator.validate(invoice_data)

    def submit(self, signed_xml, provider_config):
        import requests
        import base64

        base_url = self.get_api_base_url(provider_config)
        url = f"{base_url}/core/v1/invoices"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-KEY": provider_config.api_key or "",
        }

        payload = {
            "invoice": base64.b64encode(signed_xml.encode("utf-8")).decode("utf-8")
        }

        response = requests.post(url, json=payload, headers=headers)
        return response

    def check_status(self, submission_id, provider_config):
        import requests

        base_url = self.get_api_base_url(provider_config)
        url = f"{base_url}/core/v1/invoices/{submission_id}/status"

        headers = {
            "Accept": "application/json",
            "API-KEY": provider_config.api_key or "",
        }

        response = requests.get(url, headers=headers)
        return response

    def generate_csr(self, provider_config):
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend
        import datetime

        private_key = ec.generate_private_key(ec.SECP256K1, default_backend())

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "SA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, provider_config.company),
            x509.NameAttribute(NameOID.COMMON_NAME, provider_config.tax_id),
        ])

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(subject)
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        return {
            "csr": csr.public_bytes().decode("utf-8"),
            "private_key": private_key.private_bytes(
                encoding=private_key.private_bytes,
                format=private_key.private_bytes,
                encryption_algorithm=private_key.private_bytes,
            ),
        }

    def get_compliance_csid(self, csr_content, provider_config):
        import requests
        import base64

        base_url = self.get_api_base_url(provider_config)
        url = f"{base_url}/core/v1/csids/compliance"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-KEY": provider_config.api_key or "",
        }

        payload = {
            "csr": base64.b64encode(csr_content.encode("utf-8")).decode("utf-8")
        }

        response = requests.post(url, json=payload, headers=headers)
        return response

    def get_production_csid(self, compliance_csid, provider_config):
        import requests
        import base64

        base_url = self.get_api_base_url(provider_config)
        url = f"{base_url}/core/v1/csids/production"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-KEY": provider_config.api_key or "",
        }

        payload = {
            "compliance_request_id": compliance_csid
        }

        response = requests.post(url, json=payload, headers=headers)
        return response
