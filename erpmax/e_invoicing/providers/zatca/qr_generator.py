import base64
from io import BytesIO
from lxml import etree
import qrcode


class ZATCAQRGenerator:

    TLV_TAGS = {
        "seller_name": 1,
        "vat_number": 2,
        "time_stamp": 3,
        "invoice_total": 4,
        "total_vat": 5,
    }

    def generate(self, invoice_data):
        tlv_data = self._build_tlv(invoice_data)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(tlv_data, optimize=0)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _build_tlv(self, data):
        tlv_parts = []

        fields = [
            ("seller_name", data.get("seller", {}).get("name", "")),
            ("vat_number", data.get("seller", {}).get("vat_number", "")),
            ("time_stamp", f"{data.get('issue_date', '')}T{data.get('issue_time', '')}"),
            ("invoice_total", f"{data.get('grand_total', 0):.2f}"),
            ("total_vat", f"{data.get('total_vat', 0):.2f}"),
        ]

        for tag_name, value in fields:
            value_bytes = value.encode("utf-8")
            tlv_parts.append(bytes([self.TLV_TAGS[tag_name]]))
            tlv_parts.append(bytes([len(value_bytes)]))
            tlv_parts.append(value_bytes)

        result = b"".join(tlv_parts)
        return base64.b64encode(result).decode("utf-8")

    def generate_base64_tlv(self, data):
        return self._build_tlv(data)
