import frappe
from frappe import _
def flt(v): return round(float(v or 0), 2)
def execute(f=None):
    cols = [{"label":_("Account"),"fieldname":"account","fieldtype":"Data","width":300},{"label":_("Balance"),"fieldname":"balance","fieldtype":"Currency","width":150}]
    co = f.get("company") if f else None
    ad = f.get("as_on_date") if f else None
    if not all([co, ad]): return cols, []
    data = []
    def _bal(acc):
        r = frappe.db.sql("""SELECT COALESCE(SUM(debit-credit),0) FROM `tabJournal Entry Account` jea JOIN `tabJournal Entry` je ON je.name=jea.parent WHERE jea.account=%s AND je.docstatus=1 AND je.posting_date<=%s AND je.company=%s""", (acc, ad, co))[0][0]
        return flt(r)
    for section, types in [("Assets",["Asset","Fixed Asset","Current Asset","Bank","Cash","Receivable","Stock"]),("Liabilities",["Liability","Current Liability","Payable"]),("Equity",["Equity","Capital","Retained Earnings"])]:
        accs = frappe.db.get_all("Account",{"company":co,"account_type":["in",types],"is_group":0},pluck="name")
        if accs:
            data.append({"account":"<b>"+section+"</b>"})
            for a in accs:
                data.append({"account":a,"balance":_bal(a)})
    return cols, data