import base64
from io import BytesIO
import qrcode


class FBRQRGenerator:

    def generate(self, fbr_invoice_number):
        if not fbr_invoice_number:
            return ""

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(str(fbr_invoice_number))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
