import frappe


def after_install():
    create_default_country_profiles()


def create_default_country_profiles():
    profiles = [
        {
            "country_code": "SA",
            "country_name": "Saudi Arabia",
            "provider_type": "ZATCA",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "ECDSA-SHA256",
            "qr_encoding": "TLV",
            "api_base_url_sandbox": "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer",
            "api_base_url_production": "https://gw-fatoora.zatca.gov.sa/e-invoicing",
            "vat_rate": 15,
            "invoice_retention_years": 6,
            "requires_clearance": 1,
            "standard_invoice_limit": 1000,
            "is_default": 1,
        },
        {
            "country_code": "EG",
            "country_name": "Egypt",
            "provider_type": "ETA",
            "xml_format": "ETA JSON",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "JSON",
            "api_base_url_sandbox": "https://sandbox-api.invoicing.eta.gov.eg",
            "api_base_url_production": "https://api.invoicing.eta.gov.eg",
            "vat_rate": 14,
            "invoice_retention_years": 5,
            "is_default": 0,
        },
        {
            "country_code": "AE",
            "country_name": "United Arab Emirates",
            "provider_type": "FTA",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "Base64",
            "api_base_url_sandbox": "https://sandbox.fta.gov.ae",
            "api_base_url_production": "https://api.fta.gov.ae",
            "vat_rate": 5,
            "invoice_retention_years": 5,
            "is_default": 0,
        },
        {
            "country_code": "JO",
            "country_name": "Jordan",
            "provider_type": "ISTD",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "None",
            "api_base_url_sandbox": "",
            "api_base_url_production": "",
            "vat_rate": 16,
            "invoice_retention_years": 5,
            "is_default": 0,
        },
        {
            "country_code": "BH",
            "country_name": "Bahrain",
            "provider_type": "NBR",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "None",
            "api_base_url_sandbox": "",
            "api_base_url_production": "",
            "vat_rate": 10,
            "invoice_retention_years": 5,
            "is_default": 0,
        },
        {
            "country_code": "OM",
            "country_name": "Oman",
            "provider_type": "Generic",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "None",
            "api_base_url_sandbox": "",
            "api_base_url_production": "",
            "vat_rate": 5,
            "invoice_retention_years": 5,
            "is_default": 0,
        },
        {
            "country_code": "MA",
            "country_name": "Morocco",
            "provider_type": "Generic",
            "xml_format": "UBL 2.1",
            "signing_algorithm": "RSA-SHA256",
            "qr_encoding": "None",
            "api_base_url_sandbox": "",
            "api_base_url_production": "",
            "vat_rate": 20,
            "invoice_retention_years": 10,
            "is_default": 0,
        },
    ]

    for profile in profiles:
        if not frappe.db.exists("EH Country Profile", {"country_code": profile["country_code"]}):
            doc = frappe.get_doc(doctype="EH Country Profile", **profile)
            doc.insert()
