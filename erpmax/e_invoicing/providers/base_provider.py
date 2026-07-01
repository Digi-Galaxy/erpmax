from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate_xml(self, invoice_data):
        pass

    @abstractmethod
    def sign_invoice(self, xml_content, certificate, private_key):
        pass

    @abstractmethod
    def generate_qr(self, invoice_data, signed_xml=None):
        pass

    @abstractmethod
    def validate(self, invoice_data):
        pass

    @abstractmethod
    def submit(self, signed_xml, provider_config):
        pass

    @abstractmethod
    def check_status(self, submission_id, provider_config):
        pass

    @abstractmethod
    def generate_csr(self, provider_config):
        pass

    @abstractmethod
    def get_compliance_csid(self, csr_content, provider_config):
        pass

    @abstractmethod
    def get_production_csid(self, compliance_csid, provider_config):
        pass
