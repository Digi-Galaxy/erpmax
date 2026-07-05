import frappe
from frappe import _
def flt(v): return round(float(v or 0), 2)
def execute(f=None):
    cols = [{"label":_("Date"),"fieldname":"posting_date","fieldtype":"Date","width":100},{"label":_("Voucher Type"),"fieldname":"voucher_type","fieldtype":"Data","width":120},{"label":_("Voucher No"),"fieldname":"voucher_no","fieldtype":"Dynamic Link","options":"voucher_type","width":150},{"label":_("Account"),"fieldname":"account","fieldtype":"Data","width":200},{"label":_("Debit"),"fieldname":"debit","fieldtype":"Currency","width":120},{"label":_("Credit"),"fieldname":"credit","fieldtype":"Currency","width":120},{"label":_("Balance"),"fieldname":"balance","fieldtype":"Currency","width":120}]
    co = f.get("company") if f else None
    fd = f.get("from_date") if f else None
    td = f.get("to_date") if f else None
    acc = f.get("account") if f else None
    if not all([co, fd, td]): return cols, []
    cond = "je.company=%s AND je.posting_date BETWEEN %s AND %s AND je.docstatus=1"
    params = [co, fd, td]
    if acc:
        cond += " AND jea.account=%s"
        params.append(acc)
    rows = frappe.db.sql("""SELECT je.posting_date,'Journal Entry' as voucher_type,je.name as voucher_no,jea.account,jea.debit,jea.credit FROM `tabJournal Entry Account` jea JOIN `tabJournal Entry` je ON je.name=jea.parent WHERE """+cond+""" ORDER BY je.posting_date,je.name""", params, as_dict=True)
    bal = 0.0
    for r in rows:
        bal += flt(r.debit) - flt(r.credit)
        r["balance"] = bal
    return cols, rows