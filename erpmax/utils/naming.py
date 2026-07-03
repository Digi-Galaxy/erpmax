import re
from datetime import datetime

import frappe


TRANSACTION_CONFIG = {
    "Sales Invoice": {
        "prefix": "SINV",
        "source_doctype": "Customer",
        "link_field": "customer",
        "display_override_field": "customer_display_name",
        "display_field": "customer_name",
        "abbr_field": "customer_abbr",
    },
    "Proforma Invoice": {
        "prefix": "PRF",
        "source_doctype": "Customer",
        "link_field": "customer",
        "display_override_field": "customer_display_name",
        "display_field": "customer_name",
        "abbr_field": "customer_abbr",
    },
    "Purchase Invoice": {
        "prefix": "PINV",
        "source_doctype": "Supplier",
        "link_field": "supplier",
        "display_override_field": "supplier_display_name",
        "display_field": "supplier_name",
        "abbr_field": "supplier_abbr",
    },
    "Payment Entry": {
        "prefix": "PAY",
        "dynamic_party": True,
        "display_override_field": "party_display_name",
        "display_field": "party_name",
        "abbr_field": "party_abbr",
    },
    "Partner Transaction": {
        "prefix": "PTRN",
        "source_doctype": "Partner Account",
        "link_field": "partner_account",
        "display_field": "partner_name",
        "abbr_field": "partner_abbr",
    },
    "Internal Account Transaction": {
        "prefix": "IAT",
        "source_doctype": "Company",
        "link_field": "company",
        "abbr_source_field": "abbreviation",
    },
    "Journal Entry": {
        "prefix": "JV",
        "source_doctype": "Company",
        "link_field": "company",
        "abbr_source_field": "abbreviation",
    },
    "Expense Claim": {
        "prefix": "EXP",
        "link_field": "employee",
    },
    "Project": {
        "prefix": "PRJ",
        "link_field": "customer",
        "source_doctype": "Customer",
        "source_field": "customer_name",
        "fallback_field": "project_name",
    },
}


def make_abbreviation(value, fallback="TXN", max_len=4):
    text = re.sub(r"[^A-Za-z0-9 ]+", " ", (value or "")).strip()
    if not text:
        return fallback

    parts = [part for part in text.split() if part]
    if len(parts) > 1:
        abbr = "".join(part[0] for part in parts)
    else:
        abbr = re.sub(r"[^A-Za-z0-9]", "", parts[0])[:max_len]

    abbr = abbr.upper().strip()
    return abbr or fallback


def _get_doc_display_value(doctype, name, fieldname=None):
    if not name:
        return ""

    if fieldname:
        value = frappe.db.get_value(doctype, name, fieldname)
        if value:
            return value

    meta = frappe.get_meta(doctype)
    if meta.title_field:
        value = frappe.db.get_value(doctype, name, meta.title_field)
        if value:
            return value

    return name


def get_transaction_context(doc):
    config = TRANSACTION_CONFIG.get(doc.doctype)
    if not config:
        return {"display": "", "abbr": "", "prefix": "TXN", "date": _transaction_date(doc)}

    display_value = ""
    abbr_value = ""

    override_field = config.get("display_override_field")
    if override_field:
        override_value = getattr(doc, override_field, None)
        if override_value:
            display_value = override_value
            abbr_value = make_abbreviation(override_value)

    if config.get("dynamic_party"):
        if not display_value and getattr(doc, "party_type", None) and getattr(doc, "party", None):
            display_value = _get_doc_display_value(doc.party_type, doc.party)
            abbr_value = make_abbreviation(display_value)
    elif config.get("source_doctype"):
        link_value = getattr(doc, config.get("link_field", ""), None)
        if not display_value and link_value:
            display_value = _get_doc_display_value(config["source_doctype"], link_value)
            abbr_value = make_abbreviation(display_value)
            if config.get("abbr_source_field"):
                source_abbr = frappe.db.get_value(config["source_doctype"], link_value, config["abbr_source_field"])
                if source_abbr:
                    abbr_value = make_abbreviation(source_abbr)
        elif config.get("fallback_field"):
            source_value = getattr(doc, config["fallback_field"], None)
            display_value = source_value or ""
            abbr_value = make_abbreviation(display_value)
        else:
            display_value = ""
    else:
        source_value = getattr(doc, config.get("link_field", config.get("source_field", "")), None)
        if not source_value and config.get("fallback_field"):
            source_value = getattr(doc, config["fallback_field"], None)
        display_value = source_value or ""
        abbr_value = make_abbreviation(display_value)

    if not display_value:
        source_value = getattr(doc, config.get("link_field", config.get("source_field", "")), None)
        if not source_value and config.get("fallback_field"):
            source_value = getattr(doc, config["fallback_field"], None)
        display_value = source_value or ""

    if not abbr_value:
        abbr_value = make_abbreviation(display_value)

    return {
        "display": display_value,
        "abbr": abbr_value,
        "prefix": config["prefix"],
        "date": _transaction_date(doc),
    }


def sync_transaction_party_fields(doc):
    config = TRANSACTION_CONFIG.get(doc.doctype)
    if not config:
        return

    context = get_transaction_context(doc)
    override_field = config.get("display_override_field")
    display_field = config.get("display_field")
    abbr_field = config.get("abbr_field")

    if override_field and getattr(doc, override_field, None):
        context["display"] = getattr(doc, override_field)
        context["abbr"] = make_abbreviation(context["display"])

    if display_field and context["display"]:
        setattr(doc, display_field, context["display"])

    if abbr_field and context["abbr"]:
        setattr(doc, abbr_field, context["abbr"])


def autoname_transaction(doc):
    context = get_transaction_context(doc)
    abbr = context["abbr"] or make_abbreviation(getattr(doc, "company", None) or doc.doctype)
    dt = context["date"]
    
    # Add payment direction for Payment Entry
    direction = ""
    if doc.doctype == "Payment Entry":
        payment_type = getattr(doc, "payment_type", None)
        if payment_type == "Receive":
            direction = "-REC"
        elif payment_type == "Pay":
            direction = "-PAY"
    
    seq = _next_transaction_sequence(doc.doctype, abbr, dt)
    doc.name = f"{abbr}{direction}-{dt:%m}-{dt:%y}-{seq:04d}"


def _transaction_date(doc):
    for fieldname in ("posting_date", "expense_date", "start_date", "transaction_date"):
        value = getattr(doc, fieldname, None)
        if value:
            if isinstance(value, datetime):
                return value
            if hasattr(value, "strftime"):
                return value
            return datetime.strptime(str(value), "%Y-%m-%d")
    return datetime.now()


def _next_transaction_sequence(doctype, abbr, dt):
    # Match both: ABBR-MM-YY-NNNN and ABBR-REC/PAY-MM-YY-NNNN
    pattern = f"{abbr}%-{dt:%m}-{dt:%y}-%"
    rows = frappe.db.sql(
        f"select name from `tab{doctype}` where name like %s",
        pattern,
        as_dict=True,
    )
    highest = 0
    for row in rows:
        tail = row["name"].rsplit("-", 1)[-1]
        if tail.isdigit():
            highest = max(highest, int(tail))
    return highest + 1


def get_transaction_naming_series(doctype):
    config = TRANSACTION_CONFIG.get(doctype)
    if config:
        return config.get("prefix", "TXN")
    return "TXN"
