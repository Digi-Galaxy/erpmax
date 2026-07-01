import frappe
from ..providers import get_provider_for_country


class InvoiceService:

    def create_einvoice_from_sales_invoice(self, sales_invoice):
        si = frappe.get_doc("Sales Invoice", sales_invoice)
        company = frappe.get_doc("Company", si.company)

        provider_config = frappe.get_doc(
            "EH Provider Config", {"company": si.company}
        )
        profile = frappe.get_doc(
            "EH Country Profile", provider_config.country_profile
        )

        provider = get_provider_for_country(profile.country_code)

        invoice_data = self._prepare_invoice_data(si, company)
        validation = provider.validate(invoice_data)

        einvoice = frappe.get_doc({
            "doctype": "EH E-Invoice",
            "invoice_type": self._determine_type(si),
            "status": "Draft",
            "erpnext_invoice_type": "Sales Invoice",
            "erpnext_invoice": si.name,
            "company": si.company,
            "customer": si.customer,
            "country_profile": profile.name,
            "provider_config": provider_config.name,
            "posting_date": si.posting_date,
            "currency": si.currency,
            "grand_total": si.grand_total,
            "total_vat": si.total_tax,
        })

        if not validation["valid"]:
            einvoice.status = "Failed"
            einvoice.validation_results = "\n".join(validation["errors"])
            einvoice.has_warnings = True
            einvoice.insert()
            return einvoice

        if validation.get("warnings"):
            einvoice.has_warnings = True

        xml_content = provider.generate_xml(invoice_data)
        einvoice.validate()
        einvoice.status = "Validated"
        einvoice.save()

        return einvoice

    def _prepare_invoice_data(self, si, company):
        customer = frappe.get_doc("Customer", si.customer)
        seller_address = {
            "street": company.address_line1 or "",
            "building_number": company.address_line2 or "",
            "city": company.city or "",
            "postal_code": company.zip_code or "",
            "district": company.state or "",
        }

        buyer_address = {}
        if si.shipping_address:
            addr = frappe.get_doc("Address", si.shipping_address)
            buyer_address = {
                "street": addr.address_line1 or "",
                "building_number": addr.address_line2 or "",
                "city": addr.city or "",
                "postal_code": addr.pincode or "",
            }

        lines = []
        taxes = {}
        for item in si.items:
            lines.append({
                "name": item.item_name,
                "quantity": item.qty,
                "unit": "EA",
                "unit_price": item.rate,
                "net_amount": item.amount,
                "tax_category": item.zatca_tax_category or "S",
                "tax_rate": item.tax_rate or 0,
            })

        return {
            "invoice_number": si.name,
            "invoice_type": "Standard",
            "uuid": si.name,
            "issue_date": si.posting_date,
            "issue_time": "",
            "currency": si.currency or "SAR",
            "seller": {
                "name": company.company_name,
                "vat_number": company.vat_number,
                "address": seller_address,
            },
            "buyer": {
                "name": customer.customer_name,
                "vat_number": customer.vat_number,
                "address": buyer_address,
                "country": "SA",
            },
            "lines": lines,
            "net_total": si.total or 0,
            "tax_exclusive": (si.total or 0) - (si.total_tax or 0),
            "grand_total": si.total or 0,
            "total_vat": si.total_tax or 0,
            "payable_amount": si.outstanding_amount or (si.grand_total or 0),
            "taxes": [{"amount": si.total_tax or 0, "rate": 15, "category": "S", "taxable_amount": si.total or 0}],
        }

    def _determine_type(self, si):
        if si.is_return:
            return "Credit Note"
        if si.invoice_type == "Simplified":
            return "Simplified"
        return "Standard"
