import frappe
from frappe.utils import flt, formatdate
import re


STANDARD_RATE = "Goods at standard rate (default)"
REDUCED_RATE = "Goods at Reduced Rate"
THIRD_SCHEDULE = "3rd Schedule Goods"

STANDARD_SCENARIOS = {"SN001", "SN002", "SN026"}
REDUCED_SCENARIOS = {"SN005", "SN028"}
THIRD_SCHEDULE_SCENARIOS = {"SN008", "SN027"}


class FBRPayloadBuilder:

    def build(self, data):
        invoice_type = "Credit Note" if data.get("is_return") else "Sale Invoice"
        sandbox = data.get("_sandbox", False)
        first_sale_type = data.get("items", [{}])[0].get("sale_type", "")

        payload = {
            "invoiceType": invoice_type,
            "invoiceDate": data.get("posting_date", ""),
            "sellerNTNCNIC": data.get("seller", {}).get("tax_id", ""),
            "sellerBusinessName": data.get("seller", {}).get("name", ""),
            "sellerProvince": data.get("seller", {}).get("province", ""),
            "sellerAddress": data.get("seller", {}).get("address", ""),
            "buyerNTNCNIC": data.get("buyer", {}).get("tax_id", ""),
            "buyerBusinessName": data.get("buyer", {}).get("name", ""),
            "buyerProvince": data.get("buyer", {}).get("province", ""),
            "buyerAddress": data.get("buyer", {}).get("address", ""),
            "buyerRegistrationType": "Registered" if data.get("buyer", {}).get("tax_id") else "Unregistered",
            "invoiceRefNo": data.get("invoice_ref_no", ""),
            "items": self._build_items(data),
        }

        if sandbox and first_sale_type:
            payload["scenarioId"] = self._get_scenario_id(first_sale_type)

        return payload

    def _build_items(self, data):
        items = []
        for row in data.get("items", []):
            tax_rate = flt(row.get("tax_rate", 0))
            value_excl_st = flt(row.get("net_amount", 0))
            sales_tax = round((tax_rate * value_excl_st) / 100.0, 2) if tax_rate else 0

            sale_type = row.get("sale_type", "")
            scenario_id = self._get_scenario_id(sale_type)
            payload_sale_type = self._map_sale_type(sale_type, scenario_id)

            items.append({
                "hsCode": row.get("hs_code", ""),
                "productDescription": row.get("description", row.get("name", "")),
                "rate": self._format_rate(tax_rate),
                "uoM": row.get("uom", "Nos"),
                "quantity": flt(row.get("quantity", 0)),
                "totalValues": 0.00,
                "valueSalesExcludingST": value_excl_st,
                "fixedNotifiedValueOrRetailPrice": flt(row.get("retail_price", 0)),
                "salesTaxApplicable": sales_tax,
                "salesTaxWithheldAtSource": flt(row.get("tax_withheld", 0)),
                "extraTax": flt(row.get("extra_tax", 0)),
                "furtherTax": flt(row.get("further_tax", 0)),
                "sroScheduleNo": row.get("sro_schedule_no", ""),
                "fedPayable": flt(row.get("fed", 0)),
                "discount": abs(flt(row.get("discount", 0))),
                "saleType": payload_sale_type,
                "sroItemSerialNo": row.get("sro_item_serial", ""),
            })
        return items

    def _format_rate(self, rate):
        value = flt(rate)
        if value == 0:
            return "Exempt"
        if value.is_integer():
            return f"{int(value)}%"
        return f"{value}%"

    def _get_scenario_id(self, sale_type_name):
        if not sale_type_name:
            return ""
        try:
            return frappe.db.get_value("FBR Sale Type", sale_type_name, "scenario_id") or ""
        except Exception:
            return ""

    def _map_sale_type(self, sale_type, scenario_id):
        if scenario_id in STANDARD_SCENARIOS:
            return STANDARD_RATE
        if scenario_id in REDUCED_SCENARIOS:
            return REDUCED_RATE
        if scenario_id in THIRD_SCHEDULE_SCENARIOS:
            return THIRD_SCHEDULE
        return sale_type or STANDARD_RATE
