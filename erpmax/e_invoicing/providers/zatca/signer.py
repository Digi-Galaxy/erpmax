from lxml import etree
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend


class ZATCASigner:

    def sign(self, xml_content, certificate_pem, private_key_pem):
        private_key = load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )

        doc = etree.fromstring(xml_content)

        nsmap = {
            "ds": "http://www.w3.org/2000/09/xmldsig#",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "sig": "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2",
            "sac": "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2",
            "sbc": "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2",
        }

        def _get_qname(tag, ns="ds"):
            return f"{{{nsmap[ns]}}}{tag}"

        ext = etree.SubElement(doc, _get_qname("UBLExtensions", "ext"), nsmap={
            "ext": nsmap["ext"],
        } if "ext" not in doc.nsmap else {})

        ext_child = etree.SubElement(ext, _get_qname("UBLExtension", "ext"))
        ext_content = etree.SubElement(ext_child, _get_qname("ExtensionContent", "ext"))

        sig = etree.SubElement(ext_content, _get_qname("Signature", "sig"), nsmap={
            "sig": nsmap["sig"],
            "sac": nsmap["sac"],
            "sbc": nsmap["sbc"],
        })

        signer_party = etree.SubElement(sig, _get_qname("SignerParty", "sac"))
        party_id = etree.SubElement(signer_party, _get_qname("PartyID", "sbc"))
        party_id.text = certificate_pem

        digest = hashlib.sha256(xml_content.encode("utf-8")).digest()
        signature = private_key.sign(digest, ec.ECDSA(hashes.SHA256()))

        sign = etree.SubElement(sig, _get_qname("Signature", "sac"))
        etree.SubElement(sign, _get_qname("ID", "sbc")).text = "id1"
        etree.SubElement(sign, _get_qname("SigningTime", "sbc")).text = "2024-01-01T00:00:00"

        sig_value = etree.SubElement(sign, _get_qname("SignatureValue", "sbc"))
        sig_value.text = base64.b64encode(signature).decode("utf-8")

        signed_xml = etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return signed_xml

    def sign_hash(self, hash_bytes, private_key_pem):
        private_key = load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )
        signature = private_key.sign(hash_bytes, ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode("utf-8")
