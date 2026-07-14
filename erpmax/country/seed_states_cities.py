import json
import gzip
import os
import io
import frappe
import requests


STATES_URL = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/states.json"
CITIES_GZ_URL = "https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-cities.json.gz"


def download_states_cities_json():
    """Download dr5hn states (raw) + cities (release gz) and save as JSON files."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    states_path = os.path.join(data_dir, "states.json")
    cities_path = os.path.join(data_dir, "cities.json")

    frappe_countries = {c["name"].lower(): c["name"] for c in frappe.get_all("Country", fields=["name"])}

    def find_frappe_country(name, iso2):
        key = name.lower()
        if key in frappe_countries:
            return frappe_countries[key]
        for fc_lower, fc_name in frappe_countries.items():
            if fc_lower.startswith(key) or key.startswith(fc_lower):
                return fc_name
        return name

    print("Downloading states.json...")
    resp = requests.get(STATES_URL, timeout=120)
    resp.raise_for_status()
    raw_states = resp.json()
    print(f"Loaded {len(raw_states)} raw states")

    states = []
    seen = set()
    for s in raw_states:
        state_name = s.get("name", "").strip()
        if not state_name:
            continue
        country_name = find_frappe_country(s.get("country_name", ""), s.get("country_iso2", ""))
        key = f"{state_name}|{country_name}"
        if key in seen:
            continue
        seen.add(key)
        states.append({
            "name": state_name,
            "state_name": state_name,
            "state_code": s.get("state_code", ""),
            "country": country_name,
        })

    with open(states_path, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(states)} states to {states_path}")

    print("Downloading json-cities.json.gz (~18MB)...")
    resp = requests.get(CITIES_GZ_URL, timeout=300, stream=True)
    resp.raise_for_status()
    raw = resp.content
    print(f"Downloaded {len(raw)} bytes, decompressing...")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
        raw_cities = json.load(gz)
    print(f"Loaded {len(raw_cities)} raw cities, processing...")

    cities = []
    seen = set()
    for c in raw_cities:
        city_name = c.get("name", "").strip()
        if not city_name:
            continue
        state_name = c.get("state_name", "").strip()
        country_name = find_frappe_country(c.get("country_name", ""), c.get("country_iso2", ""))
        key = f"{city_name}|{state_name}|{country_name}"
        if key in seen:
            continue
        seen.add(key)
        cities.append({
            "name": city_name,
            "city_name": city_name,
            "state": state_name,
            "country": country_name,
        })

    with open(cities_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cities)} cities to {cities_path}")

    frappe.cache().delete_value("erpmax_states")
    frappe.cache().delete_value("erpmax_cities")
    print("Cache cleared. Virtual City/State doctypes ready.")
