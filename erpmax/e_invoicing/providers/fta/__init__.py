from ..base_provider import BaseProvider


class FTAProvider(BaseProvider):

    def generate_xml(self, invoice_data):
        raise NotImplementedError("FTA provider not yet implemented")

    def sign_invoice(self, xml_content, certificate, private_key):
        raise NotImplementedError("FTA provider not yet implemented")

    def generate_qr(self, invoice_data, signed_xml=None):
        raise NotImplementedError("FTA provider not yet implemented")

    def validate(self, invoice_data):
        raise NotImplementedError("FTA provider not yet implemented")

    def submit(self, signed_xml, provider_config):
        raise NotImplementedError("FTA provider not yet implemented")

    def check_status(self, submission_id, provider_config):
        raise NotImplementedError("FTA provider not yet implemented")

    def generate_csr(self, provider_config):
        raise NotImplementedError("FTA provider not yet implemented")

    def get_compliance_csid(self, csr_content, provider_config):
        raise NotImplementedError("FTA provider not yet implemented")

    def get_production_csid(self, compliance_csid, provider_config):
        raise NotImplementedError("FTA provider not yet implemented")
