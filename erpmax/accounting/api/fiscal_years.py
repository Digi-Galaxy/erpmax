import frappe
from frappe import _


@frappe.whitelist()
def get_fiscal_years():
    return frappe.db.get_all("Fiscal Year", fields=["name", "fiscal_year", "year_start_date", "year_end_date", "is_short_year", "is_closed"], order_by="year_start_date desc")


@frappe.whitelist()
def get_fiscal_year(name):
    doc = frappe.get_doc("Fiscal Year", name)
    return doc.as_dict()


@frappe.whitelist()
def create_fiscal_year(fiscal_year, year_start_date, year_end_date, is_short_year=0):
    existing = frappe.db.exists("Fiscal Year", {"fiscal_year": fiscal_year})
    if existing:
        frappe.throw(_("Fiscal Year {0} already exists").format(fiscal_year))
    doc = frappe.get_doc({
        "doctype": "Fiscal Year",
        "fiscal_year_name": fiscal_year,
        "fiscal_year": fiscal_year,
        "year_start_date": year_start_date,
        "year_end_date": year_end_date,
        "is_short_year": int(is_short_year),
    })
    doc.flags.ignore_permissions = True
    doc.insert()
    return doc.as_dict()


@frappe.whitelist()
def close_fiscal_year(name, close_date=None):
    doc = frappe.get_doc("Fiscal Year", name)
    if doc.is_closed:
        frappe.throw(_("Fiscal Year {0} is already closed").format(name))

    if not close_date:
        close_date = frappe.utils.nowdate()

    income_accounts = frappe.db.get_all("Account", filters={"root_type": "Income"}, pluck="name")
    expense_accounts = frappe.db.get_all("Account", filters={"root_type": "Expense"}, pluck="name")

    retained = frappe.db.get_value("Account", {"account_name": ["in", ["Retained Earnings", "Profit and Loss Account", "\u0627\u0644\u0623\u0631\u0628\u0627\u062d \u0627\u0644\u0645\u062d\u062a\u062c\u0632\u0629"]]}, "name")
    if not retained:
        frappe.throw(_("No Retained Earnings or Profit and Loss account found"))

    total_income = 0.0
    total_expense = 0.0

    for acct in income_accounts:
        bal = _get_account_balance(acct, doc.year_start_date, close_date)
        total_income += bal

    for acct in expense_accounts:
        bal = _get_account_balance(acct, doc.year_start_date, close_date)
        total_expense += bal

    net = round(total_income - total_expense, 2)

    if net == 0:
        doc.db_set("is_closed", 1)
        return {"closed": True, "message": "No net profit to close"}

    accounts = []
    for acct in income_accounts:
        bal = _get_account_balance(acct, doc.year_start_date, close_date)
        if bal > 0:
            accounts.append({"account": acct, "debit": abs(bal), "credit": 0})
    for acct in expense_accounts:
        bal = _get_account_balance(acct, doc.year_start_date, close_date)
        if bal > 0:
            accounts.append({"account": acct, "debit": 0, "credit": abs(bal)})

    if net > 0:
        accounts.append({"account": retained, "debit": 0, "credit": net})
    else:
        accounts.append({"account": retained, "debit": abs(net), "credit": 0})

    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": close_date,
        "entry_type": "Closing Entry",
        "accounts": accounts,
    })
    je.flags.ignore_permissions = True
    je.insert()
    je.submit()

    doc.db_set("is_closed", 1)

    return {"closed": True, "journal_entry": je.name, "net_profit": net}


@frappe.whitelist()
def reopen_fiscal_year(name):
    doc = frappe.get_doc("Fiscal Year", name)
    doc.db_set("is_closed", 0)
    return {"success": True}


def _get_account_balance(account, from_date, to_date):
    rows = frappe.db.sql("""
        SELECT SUM(jad.debit) - SUM(jad.credit) as balance
        FROM `tabJournal Entry Account` jad
        JOIN `tabJournal Entry` je ON je.name = jad.parent
        WHERE jad.account = %s
          AND je.docstatus = 1
          AND je.posting_date BETWEEN %s AND %s
    """, (account, from_date, to_date), as_dict=1)
    return rows[0]["balance"] or 0.0
