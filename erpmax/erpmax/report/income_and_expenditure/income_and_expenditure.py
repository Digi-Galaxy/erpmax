import frappe
from frappe import _
def flt(v): return round(float(v or 0), 2)
def execute(f=None):
    cols = [{"label":_("Particulars"),"fieldname":"particulars","fieldtype":"Data","width":350},{"label":_("Amount"),"fieldname":"amount","fieldtype":"Currency","width":150},{"label":_("Total"),"fieldname":"total","fieldtype":"Currency","width":150}]
    co = f.get("company") if f else None
    fd = f.get("from_date") if f else None
    td = f.get("to_date") if f else None
    if not all([co, fd, td]): return cols, []
    inc = frappe.db.get_all("Account",{"company":co,"account_type":["in",["Income","Revenue"]],"is_group":0},pluck="name")
    exp = frappe.db.get_all("Account",{"company":co,"account_type":["in",["Expense","Cost of Goods Sold","Depreciation"]],"is_group":0},pluck="name")
    def _bal(acc):
        r = frappe.db.sql("""SELECT COALESCE(SUM(credit-debit),0) FROM `tabJournal Entry Account` jea JOIN `tabJournal Entry` je ON je.name=jea.parent WHERE jea.account=%s AND je.docstatus=1 AND je.posting_date BETWEEN %s AND %s""", (acc, fd, td))[0][0]
        return flt(r)
    data = []; ti = 0.0; te = 0.0
    data.append({"particulars":"<b>INCOME</b>"})
    for a in inc:
        b = _bal(a); ti += b
        data.append({"particulars":"  "+a,"amount":b})
    data.append({"particulars":"Total Income","total":ti})
    data.append({})
    data.append({"particulars":"<b>EXPENDITURE</b>"})
    for a in exp:
        b = _bal(a); te += b
        data.append({"particulars":"  "+a,"amount":b})
    data.append({"particulars":"Total Expenditure","total":te})
    data.append({})
    net = ti - te
    lbl = "NET SURPLUS" if net >= 0 else "NET DEFICIT"
    data.append({"particulars":"<b>"+lbl+"</b>","total":net})
    return cols, data