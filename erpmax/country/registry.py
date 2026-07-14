import json
import os

import requests
import frappe


def load_countries():
    """Load countries.json once, cache globally."""
    if not hasattr(frappe.local, "erpmax_countries"):
        path = os.path.join(os.path.dirname(__file__), "data", "countries.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                frappe.local.erpmax_countries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            frappe.local.erpmax_countries = {}
    return frappe.local.erpmax_countries


def get_country(alpha_2):
    """Get country record by ISO alpha-2 code."""
    return load_countries().get(alpha_2.upper(), {})


def get_language(alpha_2):
    """Get primary language name for a country code."""
    return get_country(alpha_2).get("language", "")


def get_currency(alpha_2):
    """Get default currency code for a country."""
    return get_country(alpha_2).get("currency", "")


def get_phone_code(alpha_2):
    """Get international calling code for a country."""
    return get_country(alpha_2).get("phone_code", "")


def get_country_name(alpha_2):
    """Get English country name by ISO code."""
    return get_country(alpha_2).get("country_name", "")


def get_timezones(alpha_2):
    """Get list of timezone strings for a country."""
    return get_country(alpha_2).get("timezones", [])


def _find_by_name(name):
    """Look up country record by English name (case-insensitive)."""
    data = load_countries()
    for rec in data.values():
        if rec.get("country_name", "").lower() == name.strip().lower():
            return rec
    return {}


@frappe.whitelist()
def get_country_info(alpha_2):
    """Get full country info as dict by ISO alpha-2 code."""
    return get_country(alpha_2)


@frappe.whitelist()
def get_country_language(alpha_2):
    """Get language name for a country by ISO alpha-2 code."""
    return get_language(alpha_2)


@frappe.whitelist()
def get_language_by_country_name(country_name):
    """Get language name by country name (for Company form dynamic label)."""
    rec = _find_by_name(country_name)
    return rec.get("language", "Local")


@frappe.whitelist()
def get_country_info_by_name(country_name):
    """Get full country info by name (language, currency, timezone, phone, etc)."""
    rec = _find_by_name(country_name)
    if not rec:
        return {}
    tz_list = rec.get("timezones", [])
    first_tz = tz_list[0] if tz_list else "UTC"
    region = rec.get("region", "")
    if rec.get("alpha_2") in ["JP", "CN", "KR", "TW"]:
        date_fmt = "YYYY-MM-DD"
    elif region == "Americas":
        date_fmt = "MM-DD-YYYY"
    else:
        date_fmt = "DD-MM-YYYY"
    return {
        "language": rec.get("language"),
        "currency": rec.get("currency"),
        "timezone": first_tz,
        "date_format": date_fmt,
        "phone_code": rec.get("phone_code"),
        "capital": rec.get("capital"),
        "region": region,
        "subregion": rec.get("subregion"),
        "alpha_2": rec.get("alpha_2"),
        "country_name": rec.get("country_name"),
    }


ID_FORMATS = {
    "PK": {"label": "CNIC", "pattern": r"^\d{5}-\d{7}-\d{1}$", "placeholder": "12345-12345678-0", "length": 15},
    "SA": {"label": "Iqama Number", "pattern": r"^\d{10}$", "placeholder": "1234567890", "length": 10},
    "AE": {"label": "Emirates ID", "pattern": r"^\d{3}-\d{4}-\d{7}-\d{1}$", "placeholder": "123-4567-1234567-1", "length": 18},
    "US": {"label": "SSN", "pattern": r"^\d{3}-\d{2}-\d{4}$", "placeholder": "123-45-6789", "length": 11},
    "GB": {"label": "NIN", "pattern": r"^[A-Z]{2}\d{6}[A-Z]$", "placeholder": "AB123456C", "length": 9},
    "IN": {"label": "Aadhaar", "pattern": r"^\d{12}$", "placeholder": "123456789012", "length": 12},
    "CA": {"label": "SIN", "pattern": r"^\d{3}-\d{3}-\d{3}$", "placeholder": "123-456-789", "length": 11},
    "AU": {"label": "TFN", "pattern": r"^\d{9}$", "placeholder": "123456789", "length": 9},
    "DE": {"label": "Personal ID", "pattern": r"^[A-Z0-9]{9,11}$", "placeholder": "T220001293", "length": 11},
    "FR": {"label": "INSEE", "pattern": r"^\d{15}$", "placeholder": "123456789012345", "length": 15},
    "EG": {"label": "National ID", "pattern": r"^\d{14}$", "placeholder": "12345678901234", "length": 14},
    "BH": {"label": "CPR", "pattern": r"^\d{9}$", "placeholder": "123456789", "length": 9},
    "KW": {"label": "Civil ID", "pattern": r"^\d{12}$", "placeholder": "123456789012", "length": 12},
    "QA": {"label": "QID", "pattern": r"^\d{11}$", "placeholder": "12345678901", "length": 11},
    "OM": {"label": "Civil ID", "pattern": r"^\d{10}$", "placeholder": "1234567890", "length": 10},
    "MY": {"label": "NRIC", "pattern": r"^\d{6}-\d{2}-\d{4}$", "placeholder": "123456-12-1234", "length": 14},
    "SG": {"label": "NRIC", "pattern": r"^[STFG]\d{7}[A-Z]$", "placeholder": "S1234567A", "length": 9},
    "ID": {"label": "KTP", "pattern": r"^\d{16}$", "placeholder": "1234567890123456", "length": 16},
    "TR": {"label": "TC Kimlik", "pattern": r"^\d{11}$", "placeholder": "12345678901", "length": 11},
    "NG": {"label": "NIN", "pattern": r"^\d{11}$", "placeholder": "12345678901", "length": 11},
    "BD": {"label": "NID", "pattern": r"^\d{10,17}$", "placeholder": "1234567890123", "length": 17},
    "CN": {"label": "ID Card", "pattern": r"^\d{18}$", "placeholder": "123456789012345678", "length": 18},
}


def get_id_format(alpha_2):
    """Get ID format (label/pattern/placeholder) for a country code."""
    return ID_FORMATS.get(alpha_2.upper(), {"label": "ID Number", "pattern": r"^.+$", "placeholder": "", "length": 50})


@frappe.whitelist()
def get_id_format_by_country_name(country_name):
    """Get ID format by country name (for Staff client-side label update)."""
    from erpmax.country.registry import _find_by_name
    rec = _find_by_name(country_name)
    if not rec:
        return {"label": "ID Number", "pattern": "", "placeholder": "", "length": 50}
    alpha_2 = rec.get("alpha_2", "")
    return get_id_format(alpha_2)


def get_date_format(alpha_2):
    """Get recommended date format for a country."""
    if alpha_2 in ("JP", "CN", "KR", "TW"):
        return "YYYY-MM-DD"
    if get_country(alpha_2).get("region") == "Americas":
        return "MM-DD-YYYY"
    return "DD-MM-YYYY"


@frappe.whitelist()
def get_states(country=None):
    """Return list of states for a given country name (case-insensitive)."""
    data = _load_states_data()
    if not country:
        return data
    country_lower = country.strip().lower()
    return [s for s in data if s.get("country", "").lower() == country_lower]


@frappe.whitelist()
def get_cities(state=None, country=None):
    """Return list of cities filtered by state and/or country (case-insensitive)."""
    data = _load_cities_data()
    results = data
    if state:
        state_lower = state.strip().lower()
        results = [c for c in results if c.get("state", "").lower() == state_lower]
    if country:
        country_lower = country.strip().lower()
        results = [c for c in results if c.get("country", "").lower() == country_lower]
    return results


@frappe.whitelist()
def geocode_city(city, state=None, country=None):
    """Look up latitude/longitude for a city via Nominatim (OpenStreetMap)."""
    query_parts = [city]
    if state:
        query_parts.append(state)
    if country:
        query_parts.append(country)
    q = ", ".join(query_parts)
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": "ERPMax/1.0"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return {"lat": data[0]["lat"], "lon": data[0]["lon"], "display_name": data[0]["display_name"]}
    except Exception:
        pass
    return None


def _load_states_data():
    import json, os
    data = frappe.cache().get_value("erpmax_states")
    if data is not None:
        return data
    path = os.path.join(os.path.dirname(__file__), "data", "states.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    frappe.cache().set_value("erpmax_states", data)
    return data


def _load_cities_data():
    import json, os
    data = frappe.cache().get_value("erpmax_cities")
    if data is not None:
        return data
    path = os.path.join(os.path.dirname(__file__), "data", "cities.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    frappe.cache().set_value("erpmax_cities", data)
    return data
