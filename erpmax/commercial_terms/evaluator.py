import frappe
from frappe.utils import flt

SAFE_FUNCTIONS = {
    "percent": lambda base, rate: flt(base) * flt(rate) / 100.0,
    "fixed": lambda amt: flt(amt),
    "max": max,
    "min": min,
    "round": round,
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


def apply_rules(doc, rules):
    results = []
    for rule in rules:
        base_amount = 0.0
        apply_on = rule.get("apply_on", "Grand Total")
        if apply_on == "Grand Total":
            base_amount = flt(doc.get("grand_total"))
        elif apply_on == "After Tax":
            base_amount = flt(doc.get("grand_total"))
        elif apply_on == "Before Tax":
            base_amount = flt(doc.get("total"))
        elif apply_on == "Item Amount":
            base_amount = sum(flt(i.get("amount", 0)) for i in (doc.get("items") or []))

        rate_or_amount = rule.get("rate_or_amount", "Rate (%)")
        if rate_or_amount == "Formula":
            calculated_amount = evaluate(rule.get("formula"), doc)
        elif rate_or_amount == "Fixed Amount":
            calculated_amount = flt(rule.get("amount"))
        else:
            rate = flt(rule.get("rate"))
            calculated_amount = base_amount * rate / 100.0

        results.append({
            "rule_label": rule.get("rule_label"),
            "rule_type": rule.get("rule_type"),
            "base_amount": base_amount,
            "rate": flt(rule.get("rate")),
            "calculated_amount": calculated_amount,
            "account": rule.get("account"),
            "party_ledger_impact": rule.get("party_ledger_impact", 0),
            "is_recoverable": rule.get("is_recoverable", 0),
            "recovery_status": "Pending" if rule.get("is_recoverable") else "",
            "template_reference": rule.get("template_reference", ""),
        })
    return results
