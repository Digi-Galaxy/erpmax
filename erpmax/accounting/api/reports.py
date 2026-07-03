import frappe
from frappe import _


@frappe.whitelist()
def trial_balance(from_date=None, to_date=None):
    if not from_date:
        from_date = frappe.utils.nowdate()
    if not to_date:
        to_date = frappe.utils.nowdate()

    accounts = frappe.db.get_all("Account", fields=["name", "account_name", "root_type", "is_group", "parent_account"], order_by="lft asc")

    result = []
    for ac in accounts:
        balance = _get_closing_balance(ac["name"], from_date, to_date)
        if balance != 0 or True:
            debit = balance if balance > 0 else 0
            credit = abs(balance) if balance < 0 else 0
            result.append({
                "account": ac["name"],
                "account_name": ac["account_name"],
                "root_type": ac["root_type"],
                "is_group": ac["is_group"],
                "debit": round(debit, 2),
                "credit": round(credit, 2),
                "balance": round(balance, 2),
            })

    total_debit = sum(r["debit"] for r in result)
    total_credit = sum(r["credit"] for r in result)

    return {
        "accounts": result,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "from_date": from_date,
        "to_date": to_date,
    }


@frappe.whitelist()
def balance_sheet(from_date=None, to_date=None):
    if not from_date:
        from_date = "2000-01-01"
    if not to_date:
        to_date = frappe.utils.nowdate()

    asset_accounts = frappe.db.get_all("Account", filters={"root_type": "Asset", "is_group": 0}, pluck="name")
    liability_accounts = frappe.db.get_all("Account", filters={"root_type": "Liability", "is_group": 0}, pluck="name")
    equity_accounts = frappe.db.get_all("Account", filters={"root_type": "Equity", "is_group": 0}, pluck="name")

    total_assets = sum(_get_closing_balance(ac, from_date, to_date) for ac in asset_accounts)
    total_liabilities = sum(_get_closing_balance(ac, from_date, to_date) for ac in liability_accounts)
    total_equity = sum(_get_closing_balance(ac, from_date, to_date) for ac in equity_accounts)

    income_accounts = frappe.db.get_all("Account", filters={"root_type": "Income", "is_group": 0}, pluck="name")
    expense_accounts = frappe.db.get_all("Account", filters={"root_type": "Expense", "is_group": 0}, pluck="name")

    total_income = sum(_get_closing_balance(ac, from_date, to_date) for ac in income_accounts)
    total_expense = sum(_get_closing_balance(ac, from_date, to_date) for ac in expense_accounts)

    net_profit = total_income - total_expense

    return {
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "total_equity": round(total_equity, 2),
        "current_year_earnings": round(net_profit, 2),
        "total_liabilities_equity": round(total_liabilities + total_equity + net_profit, 2),
        "from_date": from_date,
        "to_date": to_date,
    }


@frappe.whitelist()
def profit_and_loss(from_date=None, to_date=None):
    if not from_date:
        from_date = frappe.utils.nowdate()
    if not to_date:
        to_date = frappe.utils.nowdate()

    income_accounts = frappe.db.get_all("Account", fields=["name", "account_name"],
                                        filters={"root_type": "Income", "is_group": 0}, order_by="name asc")
    expense_accounts = frappe.db.get_all("Account", fields=["name", "account_name"],
                                         filters={"root_type": "Expense", "is_group": 0}, order_by="name asc")

    incomes = []
    total_income = 0.0
    for ac in income_accounts:
        bal = _get_closing_balance(ac["name"], from_date, to_date)
        if bal > 0 or bal < 0:
            incomes.append({"account": ac["name"], "account_name": ac["account_name"], "amount": round(bal, 2)})
            total_income += bal

    expenses = []
    total_expense = 0.0
    for ac in expense_accounts:
        bal = _get_closing_balance(ac["name"], from_date, to_date)
        if bal > 0 or bal < 0:
            expenses.append({"account": ac["name"], "account_name": ac["account_name"], "amount": round(bal, 2)})
            total_expense += bal

    net_profit = round(total_income - total_expense, 2)

    return {
        "incomes": incomes,
        "total_income": round(total_income, 2),
        "expenses": expenses,
        "total_expense": round(total_expense, 2),
        "net_profit": net_profit,
        "from_date": from_date,
        "to_date": to_date,
    }


def _get_closing_balance(account, from_date, to_date):
    rows = frappe.db.sql("""
        SELECT SUM(jad.debit) - SUM(jad.credit) as balance
        FROM `tabJournal Entry Account` jad
        JOIN `tabJournal Entry` je ON je.name = jad.parent
        WHERE jad.account = %s
          AND je.docstatus = 1
          AND je.posting_date BETWEEN %s AND %s
    """, (account, from_date, to_date), as_dict=1)
    return rows[0]["balance"] or 0.0


# Jinja method referenced in hooks.py
def get_account_balance(account, date=None):
    import frappe
    if not date:
        date = frappe.utils.nowdate()
    balance = _get_closing_balance(account, date, date)
    return balance
