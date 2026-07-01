import frappe
from frappe import _
def flt(v): return round(float(v or 0), 2)
def execute(f=None):
    cols = [
        {"label":_("Account"),"fieldname":"account","fieldtype":"Data","width":300},
        {"label":_("Debit"),"fieldname":"debit","fieldtype":"Currency","width":150},
        {"label":_("Credit"),"fieldname":"credit","fieldtype":"Currency","width":150},
        {"label":_("Balance"),"fieldname":"balance","fieldtype":"Currency","width":150},
    ]
    co = f.get("company") if f else None
    fd = f.get("from_date") if f else None
    td = f.get("to_date") if f else None
    if not all([co, fd, td]): return cols, []
    inc = frappe.db.get_all("Account",{"company":co,"account_type":["in",["Income","Revenue"]],"is_group":0},pluck="name")
    exp = frappe.db.get_all("Account",{"company":co,"account_type":["in",["Expense","Cost of Goods Sold","Depreciation","Tax Expense"]],"is_group":0},pluck="name")
    data = []
    def _bal(acc):
        r = frappe.db.sql("""SELECT COALESCE(SUM(credit-debit),0) FROM `tabJournal Entry Account` jea JOIN `tabJournal Entry` je ON je.name=jea.parent WHERE jea.account=%s AND je.docstatus=1 AND je.posting_date BETWEEN %s AND %s""", (acc, fd, td))[0][0]
        return flt(r)
    if inc:
        data.append({"account":"<b>Income</b>"})
        for a in inc:
            b = _bal(a)
            data.append({"account":a,"credit":b if b>0 else None,"debit":-b if b<0 else None,"balance":b})
    if exp:
        data.append({"account":"<b>Expenses</b>"})
        for a in exp:
            b = _bal(a)
            data.append({"account":a,"debit":b if b>0 else None,"credit":-b if b<0 else None,"balance":-b})
    return cols, data