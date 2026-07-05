import frappe
from erpmax.commercial_terms.evaluator import evaluate, apply_rules

def resolve_templates(doc, target_document):
    company = doc.get("company")
    templates = frappe.get_all("Commercial Terms Template", filters={
        "is_active": 1,
        "target_document": ["in", [target_document, "Both"]],
    })
    if company:
        templates += frappe.get_all("Commercial Terms Template", filters={
            "is_active": 1,
            "company": company,
            "target_document": ["in", [target_document, "Both"]],
        })
    seen = set()
    rules = []
    for t in frappe.get_all("Commercial Terms Template", fields=["name"], filters={
        "is_active": 1,
        "target_document": ["in", [target_document, "Both"]],
    }):
        if t.name in seen:
            continue
        seen.add(t.name)
        template = frappe.get_cached_doc("Commercial Terms Template", t.name)
        for rule in template.rules:
            rules.append(rule.as_dict())
    return sorted(rules, key=lambda r: r.get("priority", 100))

def apply_commercial_terms(doc, target_document):
    settings = frappe.get_cached_doc("ERPMax Settings")
    if not settings.get("enable_commercial_terms"):
        return
    rules = resolve_templates(doc, target_document)
    if not rules:
        return
    doc.set("applied_commercial_terms", [])
    for result in apply_rules(doc, rules):
        doc.append("applied_commercial_terms", result)

def _dispatch(target_document, event, doc, method=None):
    hook_funcs = {
        "validate": apply_commercial_terms,
    }
    func = hook_funcs.get(event)
    if func:
        func(doc, target_document)

def sales_invoice_validate(doc, method):
    _dispatch("Sales Invoice", "validate", doc)

def sales_invoice_on_submit(doc, method):
    _dispatch("Sales Invoice", "on_submit", doc)

def sales_invoice_on_cancel(doc, method):
    _dispatch("Sales Invoice", "on_cancel", doc)

def purchase_invoice_validate(doc, method):
    _dispatch("Purchase Invoice", "validate", doc)

def purchase_invoice_on_submit(doc, method):
    _dispatch("Purchase Invoice", "on_submit", doc)

def purchase_invoice_on_cancel(doc, method):
    _dispatch("Purchase Invoice", "on_cancel", doc)
