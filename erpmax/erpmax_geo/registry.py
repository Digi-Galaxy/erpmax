import json
import os
import re

import frappe
import requests


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

ID_FORMATS = {
    "PK": {
        "label": "CNIC",
        "pattern": r"^\d{5}-\d{7}-\d{1}$",
        "placeholder": "12345-1234567-1",
        "length": 15,
        "business_label": "NTN / STRN",
        "business_placeholder": "1234567-8",
    },
    "SA": {
        "label": "Iqama / National ID",
        "pattern": r"^\d{10}$",
        "placeholder": "1234567890",
        "length": 10,
        "business_label": "VAT / CR Number",
        "business_placeholder": "300000000000003",
    },
    "AE": {
        "label": "Emirates ID",
        "pattern": r"^\d{3}-\d{4}-\d{7}-\d{1}$",
        "placeholder": "784-1990-1234567-1",
        "length": 18,
        "business_label": "TRN",
        "business_placeholder": "100000000000003",
    },
    "GB": {
        "label": "National Insurance Number",
        "pattern": r"^[A-Z]{2}\d{6}[A-Z]$",
        "placeholder": "AB123456C",
        "length": 9,
        "business_label": "VAT Registration Number",
        "business_placeholder": "GB123456789",
    },
    "US": {
        "label": "SSN",
        "pattern": r"^\d{3}-\d{2}-\d{4}$",
        "placeholder": "123-45-6789",
        "length": 11,
        "business_label": "EIN / Tax ID",
        "business_placeholder": "12-3456789",
    },
    "IN": {
        "label": "Aadhaar",
        "pattern": r"^\d{12}$",
        "placeholder": "123456789012",
        "length": 12,
        "business_label": "GSTIN",
        "business_placeholder": "22AAAAA0000A1Z5",
    },
}


ADDRESS_PROFILES = {
    "PK": {
        "country": "Pakistan",
        "region_path_order": ["state", "division", "district", "subdistrict", "town", "city"],
        "visible_fields": [
            "state",
            "subdivision",
            "division",
            "district",
            "subdistrict",
            "union_council",
            "town",
            "city",
            "zip_code",
        ],
        "required_fields": ["state", "division", "district", "city", "zip_code"],
        "labels": {
            "state": "Province / State",
            "division": "Division",
            "district": "District",
            "subdistrict": "Tehsil / Subdistrict",
            "union_council": "Union Council",
            "town": "Town / Village",
            "city": "City / Post Town",
            "zip_code": "Postal Code / ZIP",
        },
        "patterns": {
            "zip_code": r"^\d{5}$",
        },
        "notes": [
            "Use province/state as the top-level administrative area.",
            "Populate division, district, and city before saving structured addresses.",
            "Union council and town are optional but useful for delivery and validation.",
        ],
    },
    "SA": {
        "country": "Saudi Arabia",
        "region_path_order": ["state", "district", "city"],
        "visible_fields": ["state", "district", "city", "zip_code", "building_no", "street_name", "additional_no"],
        "required_fields": ["state", "city", "zip_code", "building_no", "street_name"],
        "labels": {
            "state": "Region",
            "district": "District",
            "city": "City",
            "zip_code": "Postal Code",
            "building_no": "Building Number",
            "street_name": "Street Name",
            "additional_no": "Additional Number",
        },
        "patterns": {
            "zip_code": r"^\d{5}$",
        },
        "notes": ["Saudi address should favor building/street/city/postcode data."],
    },
    "DEFAULT": {
        "country": "",
        "region_path_order": ["state", "city"],
        "visible_fields": ["state", "city", "zip_code"],
        "required_fields": [],
        "labels": {
            "state": "State / Province / Region",
            "city": "City",
            "zip_code": "Postal Code / ZIP",
        },
        "patterns": {},
        "notes": [],
    },
}


def _normalize_geo_doc(doc=None, doctype=None):
    doc = doc.copy() if isinstance(doc, dict) else {}
    doctype = doctype or doc.get("doctype")
    field_map = get_geo_field_mapping(doctype=doctype)
    if not field_map:
        return doc

    for canonical, mapped_fieldname in field_map.items():
        if not mapped_fieldname or doc.get(canonical) not in (None, ""):
            continue
        value = doc.get(mapped_fieldname)
        if value not in (None, ""):
            doc[canonical] = value
    return doc


def _google_maps_key():
    settings = get_geo_settings()
    return settings.get("google_maps_api_key") or settings.get("google_places_api_key") or ""


def _google_request(url, params):
    key = _google_maps_key()
    if not key:
        return None
    params = dict(params or {})
    params["key"] = key
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": "ERPMax/1.0"}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ERPMax Geo Google Maps request failed")
        return None


_DEFAULT_GEO_SETTINGS = {
    "map_provider": "Leaflet",
    "default_radius_m": 20000,
    "autocomplete_bias_radius_m": 15000,
    "minimum_address_level": "town",
    "clamp_marker_to_boundary": 1,
    "fallback_to_osm": 1,
    "require_place_id": 0,
    "google_maps_api_key": "",
    "google_places_api_key": "",
}


def get_geo_settings():
    cache_key = "erpmax_geo_settings"
    cached = frappe.cache().get_value(cache_key)
    if cached is not None:
        return cached

    settings = _DEFAULT_GEO_SETTINGS.copy()
    try:
        for doctype_name in ("Geo Settings", "Geo"):
            if not frappe.db.exists("DocType", doctype_name):
                continue
            has_values = False
            try:
                has_values = bool(frappe.db.sql("select count(*) from `tabSingles` where doctype=%s", (doctype_name,))[0][0])
            except Exception:
                has_values = False
            if not has_values:
                continue

            for fieldname in settings.keys():
                try:
                    value = frappe.db.get_single_value(doctype_name, fieldname)
                except Exception:
                    value = None
                if value not in (None, ""):
                    settings[fieldname] = value
            break
    except Exception:
        pass

    env_key = frappe.conf.get("google_maps_api_key") or os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_PLACES_API_KEY") or ""
    if not settings.get("google_maps_api_key"):
        settings["google_maps_api_key"] = env_key
    if not settings.get("google_places_api_key"):
        settings["google_places_api_key"] = settings.get("google_maps_api_key") or env_key

    for fieldname in ("default_radius_m", "autocomplete_bias_radius_m", "clamp_marker_to_boundary", "fallback_to_osm", "require_place_id"):
        try:
            settings[fieldname] = int(settings.get(fieldname) or 0)
        except Exception:
            settings[fieldname] = 0

    frappe.cache().set_value(cache_key, settings)
    return settings


def get_geo_field_mapping(doctype=None):
    if not doctype:
        return {}
    cache_key = f"erpmax_geo_field_map::{doctype}"
    cached = frappe.cache().get_value(cache_key)
    if cached is not None:
        return cached

    field_map = {}
    try:
        parent_filters = [
            {"parenttype": "Geo Settings", "parent": "Geo Settings", "target_doctype": doctype, "enabled": 1},
            {"parenttype": "Geo", "parent": "Geo", "target_doctype": doctype, "enabled": 1},
        ]
        rows = []
        for filters in parent_filters:
            rows = frappe.db.get_all(
                "Geo Field Mapping",
                filters=filters,
                fields=[
                    "target_doctype",
                    "country_field",
                    "state_field",
                    "division_field",
                    "district_field",
                    "subdistrict_field",
                    "town_field",
                    "city_field",
                    "zip_code_field",
                    "address_line_1_field",
                    "address_line_2_field",
                    "latitude_field",
                    "longitude_field",
                    "place_id_field",
                    "map_view_field",
                    "region_field",
                    "geofence_radius_field",
                    "geofence_center_lat_field",
                    "geofence_center_lng_field",
                ],
                limit=1,
            )
            if rows:
                break
    except Exception:
        rows = []

    if rows:
        row = rows[0]
        field_map = {
            "country": row.get("country_field") or "",
            "state": row.get("state_field") or "",
            "division": row.get("division_field") or "",
            "district": row.get("district_field") or "",
            "subdistrict": row.get("subdistrict_field") or "",
            "town": row.get("town_field") or "",
            "city": row.get("city_field") or "",
            "zip_code": row.get("zip_code_field") or "",
            "address_line_1": row.get("address_line_1_field") or "",
            "address_line_2": row.get("address_line_2_field") or "",
            "latitude": row.get("latitude_field") or "",
            "longitude": row.get("longitude_field") or "",
            "place_id": row.get("place_id_field") or "",
            "map_view": row.get("map_view_field") or "",
            "region": row.get("region_field") or "",
            "geofence_radius_m": row.get("geofence_radius_field") or "",
            "geofence_center_lat": row.get("geofence_center_lat_field") or "",
            "geofence_center_lng": row.get("geofence_center_lng_field") or "",
        }

    frappe.cache().set_value(cache_key, field_map)
    return field_map


def clear_geo_caches(doctype=None):
    frappe.cache().delete_value("erpmax_geo_settings")
    if doctype:
        frappe.cache().delete_value(f"erpmax_geo_field_map::{doctype}")
        return
    try:
        for row in frappe.db.get_all("Geo Field Mapping", fields=["target_doctype"]):
            target = row.get("target_doctype")
            if target:
                frappe.cache().delete_value(f"erpmax_geo_field_map::{target}")
    except Exception:
        pass


@frappe.whitelist()
def get_doctype_fields(doctype=None):
    if not doctype:
        return []
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return []

    rows = []
    excluded = {
        "name", "owner", "creation", "modified", "modified_by", "docstatus", "idx",
        "parent", "parentfield", "parenttype", "lft", "rgt", "old_parent", "amended_from",
        "workflow_state", "_assign", "_comments", "_liked_by", "_user_tags", "_seen",
    }
    for field in meta.fields:
        if field.fieldtype in {"Section Break", "Column Break", "Tab Break", "Fold", "HTML", "Button", "Table"}:
            continue
        if not field.fieldname:
            continue
        if field.fieldname in excluded:
            continue
        label = field.label or field.fieldname
        rows.append({
            "fieldname": field.fieldname,
            "label": label,
            "fieldtype": field.fieldtype,
            "option": f"{field.fieldname} - {label}" if label and label != field.fieldname else field.fieldname,
        })
    return rows


@frappe.whitelist()
def search_geo_doctypes(doctype_txt=None, txt=None, start=0, page_len=20, filters=None):
    search_text = (doctype_txt or txt or "").strip()
    relevant_fields = (
        "country",
        "address",
        "address_line_1",
        "address_line_2",
        "state",
        "city",
        "zip_code",
        "latitude",
        "longitude",
    )

    conditions = ["df.parenttype = 'DocType'"]
    params = []
    if search_text:
        conditions.append("df.parent like %s")
        params.append(f"%{search_text}%")

    query = f"""
        select distinct df.parent
        from `tabDocField` df
        inner join `tabDocType` dt on dt.name = df.parent
        where {' and '.join(conditions)}
          and df.fieldname in ({', '.join(['%s'] * len(relevant_fields))})
          and ifnull(dt.issingle, 0) = 0
        order by df.parent
        limit %s offset %s
    """
    params.extend(list(relevant_fields))
    params.extend([int(page_len or 20), int(start or 0)])
    rows = frappe.db.sql(query, params, as_list=1)
    return [[row[0], row[0]] for row in rows]


def _normalize_text(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


_GEO_SUGGESTION_HINTS = {
    "country": ["country", "nation", "national"],
    "state": ["state", "province", "region", "governorate"],
    "division": ["division", "zone", "admin", "administrative"],
    "district": ["district", "county", "area", "countyname"],
    "subdistrict": ["subdistrict", "tehsil", "taluka", "thana", "subdivision"],
    "town": ["town", "village", "locality", "hamlet", "sector"],
    "city": ["city", "municipality", "metro", "urban", "township"],
    "zip_code": ["zip", "postal", "postcode", "pin"],
    "address_line_1": ["address", "address1", "line1", "street", "road", "house", "building", "plot"],
    "address_line_2": ["address2", "line2", "street2", "suite", "apt", "floor"],
    "latitude": ["lat", "latitude", "geo lat", "geo_lat", "center lat"],
    "longitude": ["lng", "lon", "long", "longitude", "geo lng", "geo_lon", "center lon"],
    "place_id": ["place", "placeid", "google place", "maps place"],
    "map_view": ["map", "location map", "geo map", "map view"],
    "region": ["region", "area", "territory"],
    "geofence_radius_m": ["radius", "distance", "range", "coverage"],
    "geofence_center_lat": ["centerlat", "center lat"],
    "geofence_center_lng": ["centerlng", "center lon"],
}


def _fieldtype_bonus(fieldtype, canonical):
    fieldtype = (fieldtype or "").lower()
    if canonical in {"latitude", "longitude", "geofence_center_lat", "geofence_center_lng"}:
        return 18 if fieldtype in {"float", "currency"} else 0
    if canonical == "geofence_radius_m":
        return 18 if fieldtype in {"int", "float", "currency"} else 0
    if canonical == "map_view":
        return 18 if fieldtype == "html" else 0
    if canonical in {"country", "state", "division", "district", "subdistrict", "town", "city", "zip_code", "address_line_1", "address_line_2", "place_id", "region"}:
        return 10 if fieldtype in {"data", "link", "select", "autocomplete", "small text", "long text", "text", "code"} else 0
    return 0


def _fieldtype_allowed(fieldtype, canonical):
    fieldtype = (fieldtype or "").lower()
    if canonical in {"latitude", "longitude", "geofence_center_lat", "geofence_center_lng", "geofence_radius_m"}:
        return fieldtype in {"float", "int", "currency"}
    if canonical == "map_view":
        return fieldtype == "html"
    if canonical in {"country", "state", "division", "district", "subdistrict", "town", "city", "zip_code", "address_line_1", "address_line_2", "place_id", "region"}:
        return fieldtype in {"data", "link", "select", "autocomplete", "small text", "long text", "text", "code", "read only"}
    return True


def _field_score(field, canonical):
    fieldname = field.get("fieldname") or ""
    label = field.get("label") or ""
    fieldtype = field.get("fieldtype") or ""
    if not _fieldtype_allowed(fieldtype, canonical):
        return -1

    normalized_fieldname = _normalize_text(fieldname)
    normalized_label = _normalize_text(label)
    normalized_combo = f"{normalized_fieldname}{normalized_label}"

    score = 0
    if normalized_fieldname == _normalize_text(canonical):
        score += 100
    if normalized_label == _normalize_text(canonical):
        score += 95

    hints = _GEO_SUGGESTION_HINTS.get(canonical, [])
    for hint in hints:
        hint_key = _normalize_text(hint)
        if hint_key and (hint_key in normalized_combo or normalized_combo in hint_key):
            score += 55
        elif hint_key and hint_key in normalized_label:
            score += 45
        elif hint_key and hint_key in normalized_fieldname:
            score += 35

    # Generic token overlap helps with labels like "ZIP / Postal Code" or "Province / State".
    tokens = set(re.findall(r"[a-z0-9]+", (label + " " + fieldname).lower()))
    hint_tokens = set()
    for hint in hints:
        hint_tokens.update(re.findall(r"[a-z0-9]+", hint.lower()))
    overlap = len(tokens & hint_tokens)
    score += min(overlap * 12, 36)

    score += _fieldtype_bonus(fieldtype, canonical)
    return score


def _score_to_confidence(score):
    if score >= 120:
        return "strong"
    if score >= 80:
        return "medium"
    if score >= 45:
        return "weak"
    return "manual"


@frappe.whitelist()
def suggest_geo_field_mapping(doctype=None):
    fields = get_doctype_fields(doctype=doctype)
    if not fields:
        return {}

    suggestions = {}
    for canonical in _GEO_SUGGESTION_HINTS.keys():
        chosen = ""
        best_score = 0
        for row in fields:
            score = _field_score(row, canonical)
            if score > best_score:
                best_score = score
                chosen = row.get("fieldname") or ""
        suggestions[canonical] = {
            "fieldname": chosen if best_score >= 25 else "",
            "score": best_score if best_score >= 25 else 0,
            "confidence": _score_to_confidence(best_score),
        }
    return suggestions


def _load_json(filename, default):
    cache_key = f"erpmax_geo_{filename}"
    cached = frappe.cache().get_value(cache_key)
    if cached is not None:
        return cached

    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = default

    frappe.cache().set_value(cache_key, data)
    return data


def load_countries():
    return _load_json("countries.json", {})


def load_states():
    return _load_json("states.json", [])


def load_cities():
    return _load_json("cities.json", [])


def _norm(value):
    return (value or "").strip().lower()


def _date_format_for_country(country):
    alpha_2 = country.get("alpha_2")
    if alpha_2 in {"CN", "JP", "KR", "TW"}:
        return "YYYY-MM-DD"
    if country.get("region") == "Americas":
        return "MM-DD-YYYY"
    return "DD-MM-YYYY"


def find_country(country=None, alpha_2=None):
    countries = load_countries()
    if alpha_2:
        return countries.get(alpha_2.upper(), {})

    country_name = _norm(country)
    if not country_name:
        return {}

    for code, record in countries.items():
        names = [record.get("country_name"), record.get("official_name"), record.get("native"), code]
        if country_name in {_norm(name) for name in names if name}:
            return record
    return {}


def get_id_format(alpha_2):
    return ID_FORMATS.get((alpha_2 or "").upper(), {
        "label": "ID Number",
        "pattern": r"^.+$",
        "placeholder": "",
        "length": 50,
        "business_label": "Tax ID",
        "business_placeholder": "",
    })


@frappe.whitelist()
def get_country_context(country=None, alpha_2=None):
    record = find_country(country=country, alpha_2=alpha_2)
    if not record:
        return {}

    timezones = record.get("timezones") or []
    code = record.get("alpha_2") or alpha_2 or ""
    return {
        "country": record.get("country_name"),
        "country_name": record.get("country_name"),
        "official_name": record.get("official_name"),
        "native": record.get("native"),
        "alpha_2": code,
        "alpha_3": record.get("alpha_3"),
        "numeric": record.get("numeric"),
        "language": record.get("language"),
        "currency": record.get("currency"),
        "currency_name": record.get("currency_name"),
        "currency_symbol": record.get("currency_symbol"),
        "phone_code": record.get("phone_code"),
        "timezone": timezones[0] if timezones else "UTC",
        "timezones": timezones,
        "date_format": _date_format_for_country(record),
        "capital": record.get("capital"),
        "region": record.get("region"),
        "subregion": record.get("subregion"),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "id_format": get_id_format(code),
        "address_profile": get_address_profile(country=country, alpha_2=code),
    }


def get_address_profile(country=None, alpha_2=None):
    record = find_country(country=country, alpha_2=alpha_2)
    code = (record.get("alpha_2") or alpha_2 or "").upper()
    profile = ADDRESS_PROFILES.get(code, ADDRESS_PROFILES["DEFAULT"]).copy()
    profile["alpha_2"] = code
    profile["country_name"] = record.get("country_name") or profile.get("country")
    profile["country"] = profile.get("country") or record.get("country_name")
    profile["id_format"] = get_id_format(code)
    return profile


@frappe.whitelist()
def validate_address_profile(country=None, doc=None):
    if isinstance(doc, str):
        try:
            doc = json.loads(doc)
        except Exception:
            doc = {}
    doc = _normalize_geo_doc(doc or {}, doctype=doc.get("doctype"))
    profile = get_address_profile(country=country, alpha_2=doc.get("country_alpha_2"))
    missing = []
    invalid = []

    for fieldname in profile.get("required_fields", []):
        if not _clean_component(doc.get(fieldname)):
            missing.append(fieldname)

    for fieldname, pattern in profile.get("patterns", {}).items():
        value = _clean_component(doc.get(fieldname))
        if value and pattern and not re.match(pattern, value):
            invalid.append({"fieldname": fieldname, "value": value, "pattern": pattern})

    return {"valid": not missing and not invalid, "missing": missing, "invalid": invalid, "profile": profile}


@frappe.whitelist()
def search_states(country=None, txt=None, limit=20):
    country_name = _norm(country)
    query = _norm(txt)
    rows = []
    for state in load_states():
        if country_name and _norm(state.get("country")) != country_name:
            continue
        label = state.get("state_name") or state.get("name")
        if query and query not in _norm(label):
            continue
        rows.append({
            "value": label,
            "label": label,
            "state_code": state.get("state_code"),
            "country": state.get("country"),
        })
        if len(rows) >= int(limit or 20):
            break
    return rows


@frappe.whitelist()
def search_cities(country=None, state=None, txt=None, limit=20):
    country_name = _norm(country)
    state_name = _norm(state)
    query = _norm(txt)
    rows = []
    for city in load_cities():
        if country_name and _norm(city.get("country")) != country_name:
            continue
        if state_name and _norm(city.get("state")) != state_name:
            continue
        label = city.get("city_name") or city.get("name")
        if query and query not in _norm(label):
            continue
        rows.append({
            "value": label,
            "label": label,
            "state": city.get("state"),
            "country": city.get("country"),
        })
        if len(rows) >= int(limit or 20):
            break
    return rows


@frappe.whitelist()
def validate_id(country=None, value=None, business=0):
    context = get_country_context(country=country)
    fmt = context.get("id_format") or get_id_format(context.get("alpha_2"))
    pattern = fmt.get("business_pattern") if business else fmt.get("pattern")
    if not pattern or not value:
        return {"valid": bool(value), "format": fmt}
    return {"valid": bool(re.match(pattern, value.strip())), "format": fmt}


def _clean_component(value):
    return (value or "").strip()


def _path_key(parts):
    return " / ".join(parts)


def _region_abbr(value):
    value = _clean_component(value)
    if not value:
        return ""
    return "".join(ch for ch in value.upper() if ch.isalnum())[:12]


def _address_region_components(doc=None, country=None, alpha_2=None):
    doc = _normalize_geo_doc(doc or {}, doctype=doc.get("doctype"))
    profile = get_address_profile(country=country, alpha_2=alpha_2 or doc.get("country_alpha_2"))
    country_name = profile.get("country_name") or profile.get("country") or _clean_component(doc.get("country"))
    components = []
    if country_name:
        components.append(country_name)
    for fieldname in ["state", "division", "district", "subdistrict", "town", "city"]:
        value = _clean_component(doc.get(fieldname))
        if value and value not in components:
            components.append(value)
    return components, profile


def _find_region(name):
    return frappe.db.get_value("Region", {"region_name": name}, "name")


def _create_region(name, parent_region=None, customer=None, is_group=0, notes=None):
    region = frappe.get_doc({
        "doctype": "Region",
        "region_name": name,
        "region_abbr": _region_abbr(name),
        "customer": customer,
        "parent_region": parent_region,
        "is_group": 1 if is_group else 0,
        "status": "Active",
        "notes": notes or "",
    })
    try:
        region.insert(ignore_permissions=True)
        return region.name
    except frappe.DuplicateEntryError:
        return _find_region(name) or name


@frappe.whitelist()
def resolve_region(country=None, doc=None, customer=None, create=0):
    if isinstance(doc, str):
        try:
            doc = json.loads(doc)
        except Exception:
            doc = {}
    doc = _normalize_geo_doc(doc or {}, doctype=doc.get("doctype"))
    create = str(create).lower() in {"1", "true", "yes", "y"}

    components, profile = _address_region_components(doc=doc, country=country, alpha_2=doc.get("country_alpha_2"))
    if not components:
        return {"region": "", "created": [], "path": [], "profile": profile}

    created = []
    customer = customer or doc.get("customer") or ""
    current_parent = None
    notes = "Derived from address fields: " + ", ".join([c for c in components if c])

    for idx, component in enumerate(components):
        current_name = _path_key(components[: idx + 1])
        existing = _find_region(current_name)
        if not existing and create:
            existing = _create_region(
                current_name,
                parent_region=current_parent,
                customer=customer if idx == len(components) - 1 else "",
                is_group=idx < len(components) - 1,
                notes=notes,
            )
            created.append(existing)
        current_parent = existing or current_parent

    return {
        "region": current_parent or "",
        "created": created,
        "path": components,
        "profile": profile,
    }


def _address_customer_name(doc):
    for link in doc.get("links") or []:
        if (link.get("link_doctype") or "") == "Customer" and link.get("link_name"):
            return link.get("link_name")
    return ""


@frappe.whitelist()
def bulk_resolve_region(doctype=None, names=None, company=None, create=1):
    if doctype not in {"Address", "Customer"}:
        frappe.throw("Bulk region creation is only supported for Address and Customer")
    if isinstance(names, str):
        try:
            names = json.loads(names)
        except Exception:
            names = [n.strip() for n in names.split(",") if n.strip()]
    names = names or []
    create = str(create).lower() in {"1", "true", "yes", "y"}

    results = []
    processed = 0
    created = 0
    for name in names:
        if not name:
            continue
        try:
            doc = frappe.get_doc(doctype, name)
        except Exception:
            continue
        processed += 1
        customer_value = doc.get("customer") or ""
        if doctype == "Address":
            customer_value = customer_value or _address_customer_name(doc)
        response = resolve_region(country=doc.get("country"), doc=doc.as_dict(), customer=customer_value, create=create)
        if response.get("created"):
            created += len(response.get("created") or [])
        results.append({"name": name, "region": response.get("region") or "", "created": response.get("created") or []})
        target_customer = customer_value if doctype == "Address" else (doc.get("name") if doctype == "Customer" else "")
        if target_customer and response.get("region"):
            try:
                frappe.db.set_value("Customer", target_customer, "region", response.get("region"), update_modified=False)
            except Exception:
                pass

    return {"processed": processed, "created": created, "results": results}


@frappe.whitelist()
def geocode_city(city, state=None, country=None):
    parts = [city, state, country]
    query = ", ".join([p for p in parts if p])
    if not query:
        return None
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "ERPMax/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data:
            return {
                "lat": data[0].get("lat"),
                "lon": data[0].get("lon"),
                "display_name": data[0].get("display_name"),
            }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ERPMax Geo geocode failed")
    return None


@frappe.whitelist()
def clear_geo_cache():
    for filename in ("countries.json", "states.json", "cities.json"):
        frappe.cache().delete_value(f"erpmax_geo_{filename}")
    return True


@frappe.whitelist()
def get_geo_config(doctype=None):
    settings = get_geo_settings()
    field_map = get_geo_field_mapping(doctype=doctype)
    return {
        "google_maps_api_key": settings.get("google_maps_api_key") or "",
        "google_places_api_key": settings.get("google_places_api_key") or "",
        "google_maps_enabled": bool(settings.get("google_maps_api_key") or settings.get("google_places_api_key")),
        "map_provider": settings.get("map_provider") or "Leaflet",
        "default_radius_m": settings.get("default_radius_m") or 20000,
        "autocomplete_bias_radius_m": settings.get("autocomplete_bias_radius_m") or 15000,
        "minimum_address_level": settings.get("minimum_address_level") or "town",
        "clamp_marker_to_boundary": bool(settings.get("clamp_marker_to_boundary")),
        "fallback_to_osm": bool(settings.get("fallback_to_osm")),
        "require_place_id": bool(settings.get("require_place_id")),
        "field_map": field_map,
        "nominatim_endpoint": "https://nominatim.openstreetmap.org",
    }


def _google_component(address_components, key_name):
    for component in address_components or []:
        if key_name in (component.get("types") or []):
            return component.get("long_name") or component.get("short_name") or ""
    return ""


def _google_place_row(place, details=None):
    details = details or {}
    geometry = details.get("geometry") or place.get("geometry") or {}
    location = geometry.get("location") or {}
    comps = details.get("address_components") or []
    formatted = details.get("formatted_address") or place.get("description") or place.get("formatted_address") or ""
    return {
        "lat": location.get("lat"),
        "lon": location.get("lng"),
        "display_name": formatted,
        "place_id": details.get("place_id") or place.get("place_id") or "",
        "type": (place.get("types") or [""])[0] if place.get("types") else "",
        "house_number": _google_component(comps, "street_number"),
        "road": _google_component(comps, "route"),
        "city": _google_component(comps, "locality") or _google_component(comps, "postal_town") or _google_component(comps, "administrative_area_level_2") or "",
        "state": _google_component(comps, "administrative_area_level_1"),
        "country": _google_component(comps, "country"),
        "postcode": _google_component(comps, "postal_code"),
    }


def _google_search_places(query, country=None, region_path=None, lat=None, lon=None, radius_m=None, limit=10):
    key = _google_maps_key()
    if not key or not query:
        return []

    settings = get_geo_settings()
    if not radius_m:
        radius_m = settings.get("autocomplete_bias_radius_m") or settings.get("default_radius_m") or 15000

    params = {
        "input": query,
        "types": "geocode",
        "language": "en",
    }
    if country:
        ctx = get_country_context(country=country)
        alpha_2 = ctx.get("alpha_2")
        if alpha_2:
            params["components"] = f"country:{alpha_2.lower()}"
    if lat is not None and lon is not None and radius_m:
        params["locationbias"] = f"circle:{int(radius_m)}@{lat},{lon}"

    autocomplete = _google_request("https://maps.googleapis.com/maps/api/place/autocomplete/json", params)
    if not autocomplete or autocomplete.get("status") not in {"OK", "ZERO_RESULTS"}:
        return []

    out = []
    for prediction in (autocomplete.get("predictions") or [])[: int(limit or 10)]:
        details = _google_request(
            "https://maps.googleapis.com/maps/api/place/details/json",
            {
                "place_id": prediction.get("place_id"),
                "fields": "place_id,formatted_address,geometry,address_component,name,types",
                "language": "en",
            },
        ) or {}
        row = _google_place_row(prediction, details.get("result") or {})
        if row.get("display_name"):
            out.append(row)
    return out


def _nominatim_search(query, limit=1, bounded=None, polygon_geojson=0):
    try:
        params = {"q": query, "format": "json", "limit": limit, "polygon_geojson": polygon_geojson, "addressdetails": 1}
        if bounded:
            params["bounded"] = 1
            params["viewbox"] = bounded
        resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers={"User-Agent": "ERPMax/1.0"}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ERPMax Geo Nominatim search failed")
        return []


_RADIUS_BY_LEVEL = {"state": 80000, "division": 50000, "district": 25000, "subdistrict": 10000, "town": 4000, "city": 2000}


@frappe.whitelist()
def get_region_boundary(country=None, region_path=None, doc=None):
    if isinstance(doc, str):
        try:
            doc = json.loads(doc)
        except Exception:
            doc = {}
    if doc and not region_path:
        components, _profile = _address_region_components(doc=doc, country=country, alpha_2=doc.get("country_alpha_2"))
        region_path = _path_key(components)
    if not region_path:
        return {}
    results = _nominatim_search(region_path, limit=1)
    if not results:
        return {}
    data = results[0]
    bb = data.get("boundingbox")
    lat = float(data["lat"])
    lon = float(data["lon"])
    parts = region_path.split(" / ")
    path_len = len([p for p in parts if p])
    key = "city"
    for level in ["state", "division", "district", "subdistrict", "town", "city"]:
        if path_len >= ["", "state", "division", "district", "subdistrict", "town", "city"].index(level):
            key = level
    settings = get_geo_settings()
    radius = _RADIUS_BY_LEVEL.get(key, settings.get("default_radius_m") or 20000)
    return {"lat": lat, "lon": lon, "radius": radius, "bbox": bb, "display_name": data.get("display_name"), "level": key}


@frappe.whitelist()
def search_places(query=None, country=None, region_path=None, lat=None, lon=None, limit=10, doc=None):
    if isinstance(doc, str):
        try:
            doc = json.loads(doc)
        except Exception:
            doc = {}
    doc = _normalize_geo_doc(doc or {}, doctype=doc.get("doctype"))
    if not query:
        return []

    settings = get_geo_settings()

    if doc and not region_path:
        components, _profile = _address_region_components(doc=doc, country=country, alpha_2=doc.get("country_alpha_2"))
        if components:
            region_path = _path_key(components)

    if _google_maps_key():
        boundary = get_region_boundary(country=country, region_path=region_path) if region_path else {}
        center_lat = boundary.get("lat") or lat
        center_lon = boundary.get("lon") or lon
        radius_m = boundary.get("radius") or 0
        rows = _google_search_places(query, country=country, region_path=region_path, lat=center_lat, lon=center_lon, radius_m=radius_m, limit=limit)
        if rows:
            return rows
        if not settings.get("fallback_to_osm"):
            return []
    elif not settings.get("fallback_to_osm"):
        return []

    q = query
    if country and country.lower() not in q.lower():
        q = f"{q}, {country}"
    if region_path:
        q = f"{q}, {region_path}"
    params = {"q": q, "format": "json", "limit": limit, "addressdetails": 1}
    if lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    try:
        resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers={"User-Agent": "ERPMax/1.0"}, timeout=10)
        resp.raise_for_status()
        results = resp.json()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ERPMax Geo search_places failed")
        return []
    out = []
    for r in results:
        ad = r.get("address", {})
        out.append({
            "lat": float(r["lat"]), "lon": float(r["lon"]),
            "display_name": r.get("display_name", ""),
            "place_id": r.get("place_id", ""),
            "type": r.get("type", ""),
            "house_number": ad.get("house_number", ""),
            "road": ad.get("road", ""),
            "city": ad.get("city") or ad.get("town") or ad.get("village") or "",
            "state": ad.get("state", ""),
            "country": ad.get("country", ""),
            "postcode": ad.get("postcode", ""),
        })
    return out


@frappe.whitelist()
def forward_geocode(query=None, country=None, region_path=None, lat=None, lon=None, limit=10):
    return search_places(query=query, country=country, region_path=region_path, lat=lat, lon=lon, limit=limit)


@frappe.whitelist()
def reverse_geocode(lat=None, lon=None):
    if not lat or not lon:
        return {}
    settings = get_geo_settings()
    if _google_maps_key():
        data = _google_request(
            "https://maps.googleapis.com/maps/api/geocode/json",
            {"latlng": f"{lat},{lon}", "language": "en"},
        )
        if data and data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            row = _google_place_row({}, result)
            row["display_name"] = row.get("display_name") or result.get("formatted_address", "")
            return row
        if not settings.get("fallback_to_osm"):
            return {}
    elif not settings.get("fallback_to_osm"):
        return {}
    try:
        resp = requests.get("https://nominatim.openstreetmap.org/reverse", params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}, headers={"User-Agent": "ERPMax/1.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ERPMax Geo reverse_geocode failed")
        return {}
    ad = data.get("address", {})
    return {
        "lat": float(data["lat"]), "lon": float(data["lon"]),
        "display_name": data.get("display_name", ""),
        "house_number": ad.get("house_number", ""),
        "road": ad.get("road", ""),
        "city": ad.get("city") or ad.get("town") or ad.get("village") or "",
        "state": ad.get("state", ""),
        "country": ad.get("country", ""),
        "postcode": ad.get("postcode", ""),
    }
