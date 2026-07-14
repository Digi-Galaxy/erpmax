import frappe, json, os

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
    "accounting", "onboarding", "chart_of_accounts")

def get_available_templates():
    """Return list of available COA template names."""
    if not os.path.exists(TEMPLATE_DIR):
        return []
    names = []
    for fn in sorted(os.listdir(TEMPLATE_DIR)):
        if fn.endswith(".json"):
            fp = os.path.join(TEMPLATE_DIR, fn)
            try:
                with open(fp) as f:
                    data = json.load(f)
                names.append(data.get("template_name", fn.replace(".json","")))
            except Exception:
                pass
    return names

def build_account_tree(company, template_name):
    """Create Account records from a COA template for the given company."""
    # Find the template file
    if not os.path.exists(TEMPLATE_DIR):
        frappe.throw("COA template directory not found")

    data = None
    for fn in os.listdir(TEMPLATE_DIR):
        if not fn.endswith(".json"):
            continue
        fp = os.path.join(TEMPLATE_DIR, fn)
        with open(fp) as f:
            tpl = json.load(f)
        if tpl.get("template_name") == template_name:
            data = tpl
            break

    if not data:
        frappe.throw(f"COA template {template_name} not found")

    company_abbr = frappe.db.get_value("Company", company, "abbreviation") or company[:3].upper()
    default_currency = frappe.db.get_value("Company", company, "default_currency") or "SAR"
    created = []

    def _create(entry, parent=None):
        name = entry["n"]
        if parent:
            full_name = f"{name} - {company_abbr}"
        else:
            full_name = name

        if frappe.db.exists("Account", full_name):
            return

        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": full_name,
            "parent_account": parent,
            "is_group": entry.get("g", False),
            "root_type": entry["rt"],
            "account_type": entry.get("t", ""),
            "company": company,
            "account_currency": default_currency,
        })
        doc.insert(ignore_permissions=True)
        created.append(full_name)

        for child in entry.get("c", []):
            _create(child, full_name)

    for r in data.get("accounts", []):
        _create(r, None)

    frappe.db.commit()
    return created
