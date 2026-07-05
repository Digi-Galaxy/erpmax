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
