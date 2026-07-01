import frappe
import requests
import json
from frappe.utils import flt, formatdate
from ..base_provider import BaseProvider
from .payload_builder import FBRPayloadBuilder
from .qr_generator import FBRQRGenerator
from .validator import FBRValidator


class FBRProvider(BaseProvider):

    SANDBOX_URL = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
    PRODUCTION_URL = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata"

    def __init__(self):
        self.payload_builder = FBRPayloadBuilder()
        self.qr_generator = FBRQRGenerator()
        self.validator = FBRValidator()

    def get_api_config(self, provider_config):
        sandbox = provider_config.api_base_url_sandbox or self.SANDBOX_URL
        production = provider_config.api_base_url_production or self.PRODUCTION_URL
        endpoint = sandbox if provider_config.environment == "Sandbox" else production
        return {
            "endpoint": endpoint,
            "token": provider_config.api_secret,
            "environment": provider_config.environment or "Sandbox",
        }

    def generate_xml(self, invoice_data):
        return json.dumps(self.payload_builder.build(invoice_data), indent=2)

    def sign_invoice(self, xml_content, certificate, private_key):
        return xml_content

    def generate_qr(self, invoice_data, signed_xml=None):
        fbr_invoice_no = invoice_data.get("fbr_invoice_number", "")
        return self.qr_generator.generate(fbr_invoice_no)

    def validate(self, invoice_data):
        return self.validator.validate(invoice_data)

    def submit(self, signed_xml, provider_config):
        api_cfg = self.get_api_config(provider_config)
        payload = json.loads(signed_xml)

        headers = {
            "Authorization": f"Bearer {api_cfg['token']}",
            "Content-Type": "application/json",
            "X-Client": "ERPMax FBR E-Invoicing",
        }

        try:
            response = requests.post(
                api_cfg["endpoint"],
                json=payload,
                headers=headers,
                timeout=(10, 30),
            )

            data = {}
            try:
                data = response.json() if response.text else {}
            except ValueError:
                data = {"raw": response.text}

            return {
                "success": response.ok,
                "status_code": response.status_code,
                "data": data,
                "error": "" if response.ok else response.text,
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "data": {},
                "error": str(e),
            }

    def check_status(self, submission_id, provider_config):
        frappe.msgprint("FBR does not support async status checking. Check FBR Logs.")
        return {"success": True, "data": {}}

    def generate_csr(self, provider_config):
        raise NotImplementedError("FBR uses token-based auth, not CSR")

    def get_compliance_csid(self, csr_content, provider_config):
        raise NotImplementedError("FBR uses token-based auth, not CSID")

    def get_production_csid(self, compliance_csid, provider_config):
        raise NotImplementedError("FBR uses token-based auth, not CSID")
