import frappe
from frappe.utils import flt

SAFE_FUNCTIONS = {
    "percent": lambda base, rate: flt(base) * flt(rate) / 100.0,
    "fixed": lambda amt: flt(amt),
    "max": max,
    "min": min,
    "round": round,
}

GL_MAP = {
    ("Hold", "Receive"): {"dr": "ct_account", "cr": "party_account", "outstanding": -1},
    ("Hold", "Pay"): {"dr": "party_account", "cr": "ct_account", "outstanding": 0},
    ("Deduction", "Receive"): {"dr": "ct_account", "cr": "party_account", "outstanding": -1},
    ("Deduction", "Pay"): {"dr": "party_account", "cr": "ct_account", "outstanding": 0},
    ("Addition", "Receive"): {"dr": "party_account", "cr": "ct_account", "outstanding": 1},
    ("Addition", "Pay"): {"dr": "ct_account", "cr": "party_account", "outstanding": 0},
    ("Commission", "Pay"): {"dr": "ct_account", "cr": "party_account", "outstanding": 0},
}

ACCOUNT_NAME_TEMPLATES = {
    ("Hold", "Receive"): "{label} Receivable",
    ("Hold", "Pay"): "{label} Payable",
    ("Deduction", "Receive"): "{label} Expense",
    ("Deduction", "Pay"): "{label} Income",
    ("Addition", "Receive"): "{label} Income",
    ("Addition", "Pay"): "{label} Expense",
    ("Commission", "Pay"): "{label} Payable",
}

ACCOUNT_TYPE_MAP = {
    ("Hold", "Receive"): "Receivable",
    ("Hold", "Pay"): "Payable",
    ("Deduction", "Receive"): "Expense",
    ("Deduction", "Pay"): "Income",
    ("Addition", "Receive"): "Income",
    ("Addition", "Pay"): "Expense",
    ("Commission", "Pay"): "Payable",
}

ROOT_TYPE_MAP = {
    ("Hold", "Receive"): "Asset",
    ("Hold", "Pay"): "Liability",
    ("Deduction", "Receive"): "Expense",
    ("Deduction", "Pay"): "Income",
    ("Addition", "Receive"): "Income",
    ("Addition", "Pay"): "Expense",
    ("Commission", "Pay"): "Liability",
}


def evaluate(formula, doc):
    if not formula:
        return 0.0
    if formula.strip().isdigit() or formula.strip().replace(".", "").isdigit():
        return flt(formula)
    callable_fields = {
        "grand_total": flt(doc.get("grand_total")),
        "net_total": flt(doc.get("total")),
        "total_tax": flt(doc.get("tax_total")),
        "item_qty": sum(flt(i.get("qty", 0)) for i in (doc.get("items") or [])),
        "item_amount": sum(flt(i.get("amount", 0)) for i in (doc.get("items") or [])),
        "outstanding_amount": flt(doc.get("outstanding_amount")),
    }
    allowed = {**SAFE_FUNCTIONS, **callable_fields}
    try:
        result = frappe.utils.eval(formula, allowed)
        return flt(result)
    except Exception as e:
        frappe.log_error("Commercial Terms formula error: %s - %s" % (formula, str(e)))
        return 0.0


def ensure_account(rule, doc):
    if rule.get("account"):
        return rule["account"]
    if not rule.get("auto_account", 1):
        return None
    effect = rule.get("effect", "Deduction")
    direction = rule.get("direction", "Receive")
    label = rule.get("rule_label", "Term")
    company = doc.get("company")
    if not company:
        return None
    abbr = frappe.db.get_value("Company", company, "abbr")
    account_name = ACCOUNT_NAME_TEMPLATES.get((effect, direction), "{label} Expense").format(label=label)
    full_name = "%s - %s" % (account_name, abbr)
    existing = frappe.db.get_value("Account", {"name": full_name})
    if existing:
        return existing
    root_type = ROOT_TYPE_MAP.get((effect, direction), "Expense")
    account_type = ACCOUNT_TYPE_MAP.get((effect, direction), "Expense")
    parent_account = _find_parent(company, root_type)
    if not parent_account:
        return None
    acc = frappe.get_doc({
        "doctype": "Account",
        "account_name": account_name,
        "company": company,
        "parent_account": parent_account,
        "root_type": root_type,
        "account_type": account_type,
        "is_group": 0,
    })
    acc.flags.ignore_permissions = True
    acc.insert()
    frappe.db.commit()
    return acc.name


def _find_parent(company, root_type):
    candidates = frappe.db.sql("""
        SELECT name FROM `tabAccount`
        WHERE company = %s AND root_type = %s AND is_group = 1
        ORDER BY lft ASC LIMIT 1
    """, (company, root_type))
    if candidates:
        return candidates[0][0]
    return frappe.db.get_value("Account", {"company": company, "is_group": 1}, "name")


def compute_base_amount(rule, doc):
    apply_on = rule.get("apply_on", "Grand Total")
    if apply_on == "Grand Total":
        return flt(doc.get("grand_total"))
    elif apply_on == "After Tax":
        return flt(doc.get("grand_total"))
    elif apply_on == "Before Tax":
        return flt(doc.get("total"))
    elif apply_on == "Item Amount":
        return sum(flt(i.get("amount", 0)) for i in (doc.get("items") or []))
    return 0.0


def compute_amount(base_amount, rule, doc=None):
    rate_or_amount = rule.get("rate_or_amount", "Rate (%)")
    if rate_or_amount == "Formula":
        return evaluate(rule.get("formula"), doc or {})
    elif rate_or_amount == "Fixed Amount":
        return flt(rule.get("amount"))
    else:
        rate = flt(rule.get("rate"))
        return base_amount * rate / 100.0


def apply_distribution(rule, base_amount, calculated_amount):
    dist_rows = rule.get("distribution", [])
    if not dist_rows or not any(flt(d.get("allocation_pct", 0)) for d in dist_rows):
        return [{
            "rule_label": rule.get("rule_label"),
            "effect": rule.get("effect"),
            "direction": rule.get("direction"),
            "base_amount": base_amount,
            "rate": flt(rule.get("rate")),
            "calculated_amount": calculated_amount,
            "account": rule.get("account"),
            "party_type": None,
            "party": None,
            "allocation_pct": None,
            "party_ledger_impact": rule.get("party_ledger_impact", 0),
            "is_recoverable": rule.get("is_recoverable", 0),
            "recovery_status": "Pending" if rule.get("is_recoverable") else "",
            "template_reference": rule.get("template_reference", ""),
        }]
    total_pct = sum(flt(d.get("allocation_pct", 0)) for d in dist_rows) or 100
    results = []
    for d in dist_rows:
        pct = flt(d.get("allocation_pct", 0))
        party_amt = calculated_amount * pct / total_pct
        party_rate = d.get("rate") if d.get("rate") else rule.get("rate")
        results.append({
            "rule_label": "%s - %s" % (rule.get("rule_label"), d.get("party")),
            "effect": rule.get("effect"),
            "direction": rule.get("direction"),
            "base_amount": base_amount,
            "rate": flt(party_rate),
            "calculated_amount": party_amt,
            "account": rule.get("account"),
            "party_type": d.get("party_type"),
            "party": d.get("party"),
            "allocation_pct": pct,
            "party_ledger_impact": rule.get("party_ledger_impact", 0),
            "is_recoverable": rule.get("is_recoverable", 0),
            "recovery_status": "Pending" if rule.get("is_recoverable") else "",
            "template_reference": rule.get("template_reference", ""),
        })
    return results


def apply_rules(doc, rules):
    results = []
    for rule in rules:
        base_amount = compute_base_amount(rule, doc)
        calculated_amount = compute_amount(base_amount, rule, doc)
        if not calculated_amount:
            continue
        account = ensure_account(rule, doc)
        rule["account"] = account or rule.get("account")
        for entry in apply_distribution(rule, base_amount, calculated_amount):
            results.append(entry)
    return results


def get_gl_entries_for_term(ct, debit_to):
    effect = ct.get("effect")
    direction = ct.get("direction")
    amt = flt(ct.get("calculated_amount", 0))
    ct_account = ct.get("account")
    if not amt or not ct_account:
        return [], 0
    pattern = GL_MAP.get((effect, direction))
    if not pattern:
        return [], 0
    entries = []
    outstanding_factor = pattern.get("outstanding", 0)
    outstanding_impact = outstanding_factor * amt
    party_account = debit_to
    if effect == "Commission":
        sp_account = ct.get("party") and frappe.db.get_value("Sales Person", ct.get("party"), "commission_payable_account")
        party_account = sp_account or ct_account
    if pattern["dr"] == "ct_account":
        entries.append({"account": ct_account, "debit": amt, "credit": 0})
        entries.append({"account": party_account, "debit": 0, "credit": amt})
    else:
        entries.append({"account": party_account, "debit": amt, "credit": 0})
        entries.append({"account": ct_account, "debit": 0, "credit": amt})
    return entries, outstanding_impact
