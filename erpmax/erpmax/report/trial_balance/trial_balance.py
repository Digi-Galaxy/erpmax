import frappe
from frappe import _
def flt(v): return round(float(v or 0), 2)
def execute(f=None):
    cols = [{"label":_("Account"),"fieldname":"account","fieldtype":"Data","width":300},{"label":_("Debit"),"fieldname":"debit","fieldtype":"Currency","width":150},{"label":_("Credit"),"fieldname":"credit","fieldtype":"Currency","width":150}]
    co = f.get("company") if f else None
    ad = f.get("as_on_date") if f else None
    if not all([co, ad]): return cols, []
    accs = frappe.db.get_all("Account",{"company":co,"is_group":0},pluck="name")
    data = []; td = 0.0; tc = 0.0
    for a in accs:
        r = frappe.db.sql("""SELECT COALESCE(SUM(debit),0), COALESCE(SUM(credit),0) FROM `tabJournal Entry Account` jea JOIN `tabJournal Entry` je ON je.name=jea.parent WHERE jea.account=%s AND je.docstatus=1 AND je.posting_date<=%s AND je.company=%s""", (a, ad, co))[0]
        d, c = flt(r[0]), flt(r[1])
        if d or c:
            data.append({"account":a,"debit":d,"credit":c})
            td += d; tc += c
    data.append({"account":"<b>Total</b>","debit":td,"credit":tc})
    return cols, data