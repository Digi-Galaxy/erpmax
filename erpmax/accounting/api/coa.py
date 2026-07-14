import frappe
from frappe import _
import os, json

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'coa', 'templates')

def _load_templates():
    templates = {}
    if not os.path.isdir(TEMPLATES_DIR):
        return templates
    for fname in os.listdir(TEMPLATES_DIR):
        if fname.endswith('.json'):
            key = fname.replace('.json', '').upper()
            with open(os.path.join(TEMPLATES_DIR, fname), 'r', encoding='utf-8') as f:
                templates[key] = json.load(f)
    return templates

def _get_templates_cache():
    if not hasattr(_get_templates_cache, '_cache'):
        _get_templates_cache._cache = _load_templates()
    return _get_templates_cache._cache

TEMPLATES_LIST = [
    {"key": "GAAP", "title": "US GAAP", "currency": "USD", "vat_rate": 15},
    {"key": "IFRS", "title": "International IFRS", "currency": "USD", "vat_rate": 15},
    {"key": "UK", "title": "United Kingdom", "currency": "GBP", "vat_rate": 20},
    {"key": "SKR03", "title": "Germany SKR03", "currency": "EUR", "vat_rate": 19},
    {"key": "PCG", "title": "France PCG", "currency": "EUR", "vat_rate": 20},
    {"key": "KSA", "title": "Saudi Arabia (SOCPA)", "currency": "SAR", "vat_rate": 15},
    {"key": "NGO", "title": "Non-Profit (SFAS 117)", "currency": "USD", "vat_rate": 0},
    {"key": "PK", "title": "Pakistan", "currency": "PKR", "vat_rate": 18},
    {"key": "MY", "title": "Malaysia", "currency": "MYR", "vat_rate": 6},
    {"key": "UAE", "title": "UAE", "currency": "AED", "vat_rate": 5},
]

@frappe.whitelist()
def onboard(template="GAAP"):
    COA_TEMPLATES = _get_templates_cache()
    if template not in COA_TEMPLATES:
        frappe.throw(_("Unknown COA template: {0}").format(template))
    config = COA_TEMPLATES[template]

    created = []
    for ac in config.get("accounts", []):
        existing = frappe.db.exists("Account", {"account_name": ac["account_name"]})
        if existing:
            continue
        parent_name = None
        if ac.get("parent_account"):
            parent = frappe.db.get_value("Account", {"account_name": ac["parent_account"]}, "name")
            if parent:
                parent_name = parent
        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": ac["account_name"],
            "root_type": ac["root_type"],
            "is_group": ac.get("is_group", 0),
            "account_number": ac.get("account_number"),
            "account_currency": config.get("currency", "SAR"),
            "tax_rate": ac.get("tax_rate", config.get("vat_rate", 0)),
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        if parent_name:
            frappe.db.set_value("Account", doc.name, "parent_account", parent_name)
        created.append(ac["account_name"])

    frappe.db.set_value("System Settings", None, "currency", config.get("currency", "SAR"))
    frappe.db.set_default("erpmax_coa_template", template)
    frappe.db.set_default("erpmax_currency", config.get("currency", "SAR"))
    frappe.db.set_default("erpmax_vat_rate", config.get("vat_rate", 0))

    return {"created": created, "template": template, "currency": config.get("currency", "SAR"), "total": len(created)}

@frappe.whitelist()
def get_templates():
    return TEMPLATES_LIST

@frappe.whitelist()
def get_chart_of_accounts():
    accounts = frappe.db.get_all(
        "Account",
        fields=["name", "account_name", "account_number", "account_type", "root_type",
                "parent_account", "is_group", "tax_rate", "account_currency"],
        order_by="lft asc",
    )
    tree = _build_tree(accounts)
    return {"flat": accounts, "tree": tree}

def _build_tree(flat):
    by_name = {a["name"]: {**a, "children": []} for a in flat}
    roots = []
    for a in by_name.values():
        parent = a.get("parent_account")
        if parent and parent in by_name:
            by_name[parent]["children"].append(a)
        else:
            roots.append(a)
    return roots

COA_COUNTRY_MAP = {
    "Saudi Arabia": "KSA",
    "United Arab Emirates": "UAE",
    "United States": "GAAP",
    "United Kingdom": "UK",
    "Germany": "SKR03",
    "France": "PCG",
    "Pakistan": "PK",
    "Malaysia": "MY",
}
FALLBACK_COA = "IFRS"

@frappe.whitelist()
def suggest_template(country=None):
    if not country:
        return FALLBACK_COA
    return COA_COUNTRY_MAP.get(country, FALLBACK_COA)

@frappe.whitelist()
def onboard_for_company(company, template=None):
    company_doc = frappe.get_doc("Company", company)
    tmpl = template or company_doc.coa_template or suggest_template(company_doc.country)
    result = onboard(template=tmpl)

    created = result.get("created", [])
    if not created:
        tmpl_data = _get_template_accounts(tmpl)
        created = [a["account_name"] for a in tmpl_data]

    for ac_name in created:
        ac_docname = frappe.db.get_value("Account", {"account_name": ac_name}, "name")
        if ac_docname and not frappe.db.exists("Company Account", {"parent": company, "account": ac_docname}):
            ca = frappe.get_doc({
                "doctype": "Company Account",
                "parent": company,
                "parenttype": "Company",
                "parentfield": "company_accounts",
                "account": ac_docname,
                "account_name": ac_name,
            })
            ca.flags.ignore_permissions = True
            ca.insert()

    frappe.db.commit()
    return result

def _get_template_accounts(template):
    COA_TEMPLATES = _get_templates_cache()
    config = COA_TEMPLATES.get(template)
    if config:
        return config.get("accounts", [])
    return []

@frappe.whitelist()
def get_coa_accounts(template):
    return _get_template_accounts(template)

@frappe.whitelist()
def get_template_config(template):
    COA_TEMPLATES = _get_templates_cache()
    return COA_TEMPLATES.get(template)

def _map_root_to_account_type(root_type):
    mapping = {"Asset": "Bank", "Liability": "Payable", "Income": "Income",
               "Expense": "Expense", "Equity": "Equity"}
    return mapping.get(root_type, "Other")

@frappe.whitelist()
def create_coa_for_company(company, template):
    return onboard_for_company(company, template=template)
