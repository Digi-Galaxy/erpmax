from lxml import etree
from datetime import datetime


class ZATCAXMLBuilder:
    NSMAP = {
        "ns": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "sig": "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2",
        "sac": "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2",
        "sbc": "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2",
    }

    def build(self, data):
        invoice = etree.Element(
            f"{{{self.NSMAP['ns']}}}Invoice",
            nsmap=self.NSMAP,
            attrib={
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            },
        )

        etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}UBLVersionID").text = "2.1"
        etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}CustomizationID").text = "2.0"

        profile_id = etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}ProfileID")
        profile_id.text = "reporting:1.0"
        if data.get("invoice_type") == "Standard":
            profile_id.text = "reporting:1.0"

        etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}ID").text = data.get("invoice_number", "")
        etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}UUID").text = data.get("uuid", "")

        issue_date = etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}IssueDate")
        issue_date.text = data.get("issue_date", datetime.now().strftime("%Y-%m-%d"))

        issue_time = etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}IssueTime")
        issue_time.text = data.get("issue_time", datetime.now().strftime("%H:%M:%S"))

        inv_type = etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}InvoiceTypeCode")
        if data.get("invoice_type") == "Simplified":
            inv_type.text = "388"
            inv_type.set("name", "Simplified")
        elif data.get("invoice_type") == "Credit Note":
            inv_type.text = "381"
            inv_type.set("name", "Credit Note")
        elif data.get("invoice_type") == "Debit Note":
            inv_type.text = "383"
            inv_type.set("name", "Debit Note")
        else:
            inv_type.text = "388"
            inv_type.set("name", "Standard")

        etree.SubElement(invoice, f"{{{self.NSMAP['cbc']}}}DocumentCurrencyCode").text = data.get("currency", "SAR")

        self._build_supplier_party(invoice, data)
        self._build_customer_party(invoice, data)
        self._build_tax_totals(invoice, data)
        self._build_legal_monetary_total(invoice, data)
        self._build_invoice_lines(invoice, data)

        return etree.tostring(invoice, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def _build_supplier_party(self, invoice, data):
        seller = data.get("seller", {})
        party = etree.SubElement(invoice, f"{{{self.NSMAP['cac']}}}AccountingSupplierParty")
        party_party = etree.SubElement(party, f"{{{self.NSMAP['cac']}}}Party")

        party_id = etree.SubElement(party_party, f"{{{self.NSMAP['cbc']}}}CompanyID")
        party_id.text = seller.get("vat_number", "")
        party_id.set("schemeID", "CRN")
        party_id.set("schemeAgencyID", "6")

        if seller.get("vat_number"):
            tax_scheme = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PartyTaxScheme")
            etree.SubElement(tax_scheme, f"{{{self.NSMAP['cbc']}}}CompanyID").text = seller.get("vat_number", "")
            tax_scheme_code = etree.SubElement(tax_scheme, f"{{{self.NSMAP['cac']}}}TaxScheme")
            etree.SubElement(tax_scheme_code, f"{{{self.NSMAP['cbc']}}}ID").text = "VAT"

        legal_entity = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PartyLegalEntity")
        etree.SubElement(legal_entity, f"{{{self.NSMAP['cbc']}}}RegistrationName").text = seller.get("name", "")

        address = seller.get("address", {})
        if address:
            addr = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PostalAddress")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}StreetName").text = address.get("street", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}BuildingNumber").text = address.get("building_number", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}CityName").text = address.get("city", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}PostalZone").text = address.get("postal_code", "")
            sub = etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}CountrySubentity")
            sub.text = address.get("district", "")
            country = etree.SubElement(addr, f"{{{self.NSMAP['cac']}}}Country")
            etree.SubElement(country, f"{{{self.NSMAP['cbc']}}}IdentificationCode").text = "SA"

    def _build_customer_party(self, invoice, data):
        buyer = data.get("buyer", {})
        party = etree.SubElement(invoice, f"{{{self.NSMAP['cac']}}}AccountingCustomerParty")
        party_party = etree.SubElement(party, f"{{{self.NSMAP['cac']}}}Party")

        if buyer.get("vat_number"):
            party_id = etree.SubElement(party_party, f"{{{self.NSMAP['cbc']}}}CompanyID")
            party_id.text = buyer.get("vat_number", "")
            party_id.set("schemeID", "CRN")
            party_id.set("schemeAgencyID", "6")

        tax_scheme = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PartyTaxScheme")
        if buyer.get("vat_number"):
            etree.SubElement(tax_scheme, f"{{{self.NSMAP['cbc']}}}CompanyID").text = buyer.get("vat_number", "")
        tax_code = etree.SubElement(tax_scheme, f"{{{self.NSMAP['cac']}}}TaxScheme")
        etree.SubElement(tax_code, f"{{{self.NSMAP['cbc']}}}ID").text = "VAT"

        legal_entity = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PartyLegalEntity")
        etree.SubElement(legal_entity, f"{{{self.NSMAP['cbc']}}}RegistrationName").text = buyer.get("name", "")

        address = buyer.get("address", {})
        if address:
            addr = etree.SubElement(party_party, f"{{{self.NSMAP['cac']}}}PostalAddress")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}StreetName").text = address.get("street", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}BuildingNumber").text = address.get("building_number", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}CityName").text = address.get("city", "")
            etree.SubElement(addr, f"{{{self.NSMAP['cbc']}}}PostalZone").text = address.get("postal_code", "")
            country = etree.SubElement(addr, f"{{{self.NSMAP['cac']}}}Country")
            etree.SubElement(country, f"{{{self.NSMAP['cbc']}}}IdentificationCode").text = buyer.get("country", "SA")

    def _build_tax_totals(self, invoice, data):
        taxes = data.get("taxes", [])
        if not taxes:
            return
        total = etree.SubElement(invoice, f"{{{self.NSMAP['cac']}}}TaxTotal")
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxAmount").set("currencyID", data.get("currency", "SAR"))
        total_amount = sum(t.get("amount", 0) for t in taxes)
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxAmount").text = f"{total_amount:.2f}"

        for tax in taxes:
            sub = etree.SubElement(total, f"{{{self.NSMAP['cac']}}}TaxSubtotal")
            etree.SubElement(sub, f"{{{self.NSMAP['cbc']}}}TaxableAmount").set(
                "currencyID", data.get("currency", "SAR")
            ).text = f"{tax.get('taxable_amount', 0):.2f}"
            etree.SubElement(sub, f"{{{self.NSMAP['cbc']}}}TaxAmount").set(
                "currencyID", data.get("currency", "SAR")
            ).text = f"{tax.get('amount', 0):.2f}"
            category = etree.SubElement(sub, f"{{{self.NSMAP['cac']}}}TaxCategory")
            etree.SubElement(category, f"{{{self.NSMAP['cbc']}}}ID").text = tax.get("category", "S")
            etree.SubElement(category, f"{{{self.NSMAP['cbc']}}}Percent").text = f"{tax.get('rate', 0):.2f}"
            scheme = etree.SubElement(category, f"{{{self.NSMAP['cac']}}}TaxScheme")
            etree.SubElement(scheme, f"{{{self.NSMAP['cbc']}}}ID").text = "VAT"

    def _build_legal_monetary_total(self, invoice, data):
        total = etree.SubElement(invoice, f"{{{self.NSMAP['cac']}}}LegalMonetaryTotal")
        currency = data.get("currency", "SAR")

        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}LineExtensionAmount").set("currencyID", currency)
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}LineExtensionAmount").text = f"{data.get('net_total', 0):.2f}"

        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxExclusiveAmount").set("currencyID", currency)
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxExclusiveAmount").text = f"{data.get('tax_exclusive', 0):.2f}"

        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxInclusiveAmount").set("currencyID", currency)
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}TaxInclusiveAmount").text = f"{data.get('grand_total', 0):.2f}"

        if data.get("prepaid_amount"):
            etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}PrepaidAmount").set("currencyID", currency)
            etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}PrepaidAmount").text = f"{data.get('prepaid_amount', 0):.2f}"

        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}PayableAmount").set("currencyID", currency)
        etree.SubElement(total, f"{{{self.NSMAP['cbc']}}}PayableAmount").text = f"{data.get('payable_amount', 0):.2f}"

    def _build_invoice_lines(self, invoice, data):
        for idx, line in enumerate(data.get("lines", []), 1):
            inv_line = etree.SubElement(invoice, f"{{{self.NSMAP['cac']}}}InvoiceLine")
            etree.SubElement(inv_line, f"{{{self.NSMAP['cbc']}}}ID").text = str(idx)

            etree.SubElement(inv_line, f"{{{self.NSMAP['cbc']}}}InvoicedQuantity").set("unitCode", line.get("unit", "EA"))
            etree.SubElement(inv_line, f"{{{self.NSMAP['cbc']}}}InvoicedQuantity").text = f"{line.get('quantity', 0):.2f}"

            etree.SubElement(inv_line, f"{{{self.NSMAP['cbc']}}}LineExtensionAmount").set(
                "currencyID", data.get("currency", "SAR")
            ).text = f"{line.get('net_amount', 0):.2f}"

            item = etree.SubElement(inv_line, f"{{{self.NSMAP['cac']}}}Item")
            etree.SubElement(item, f"{{{self.NSMAP['cbc']}}}Name").text = line.get("name", "")

            classified_tax = etree.SubElement(item, f"{{{self.NSMAP['cac']}}}ClassifiedTaxCategory")
            etree.SubElement(classified_tax, f"{{{self.NSMAP['cbc']}}}ID").text = line.get("tax_category", "S")
            etree.SubElement(classified_tax, f"{{{self.NSMAP['cbc']}}}Percent").text = f"{line.get('tax_rate', 0):.2f}"
            tax_scheme = etree.SubElement(classified_tax, f"{{{self.NSMAP['cac']}}}TaxScheme")
            etree.SubElement(tax_scheme, f"{{{self.NSMAP['cbc']}}}ID").text = "VAT"

            price = etree.SubElement(inv_line, f"{{{self.NSMAP['cac']}}}Price")
            etree.SubElement(price, f"{{{self.NSMAP['cbc']}}}PriceAmount").set(
                "currencyID", data.get("currency", "SAR")
            ).text = f"{line.get('unit_price', 0):.2f}"
