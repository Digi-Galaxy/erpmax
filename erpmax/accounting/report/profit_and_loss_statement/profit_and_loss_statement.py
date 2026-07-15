# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    """Profit and Loss Statement Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "account",
            "fieldtype": "Link",
            "label": _("Account"),
            "options": "Account",
            "width": 300,
        },
        {
            "fieldname": "account_name",
            "fieldtype": "Data",
            "label": _("Account Name"),
            "width": 200,
        },
        {
            "fieldname": "root_type",
            "fieldtype": "Data",
            "label": _("Type"),
            "width": 100,
        },
        {
            "fieldname": "balance",
            "fieldtype": "Currency",
            "label": _("Amount"),
            "width": 150,
        },
    ]


def get_data(filters):
    """Get profit and loss data"""
    from_date = filters.get("from_date") or frappe.utils.nowdate()
    to_date = filters.get("to_date") or frappe.utils.nowdate()
    company = filters.get("company")
    
    # Get income accounts
    income_accounts = get_accounts_by_type("Income", from_date, to_date, company)
    
    # Get expense accounts
    expense_accounts = get_accounts_by_type("Expense", from_date, to_date, company)
    
    data = []
    
    # Income section
    data.append({
        "account": "",
        "account_name": _("Income"),
        "root_type": "",
        "balance": "",
        "indent": 0,
    })
    
    total_income = 0
    for account in income_accounts:
        data.append({
            "account": account.name,
            "account_name": account.account_name,
            "root_type": "Income",
            "balance": flt(account.balance, 2),
            "indent": 1,
        })
        total_income += account.balance
    
    data.append({
        "account": "",
        "account_name": _("Total Income"),
        "root_type": "",
        "balance": flt(total_income, 2),
        "indent": 0,
    })
    
    # Expenses section
    data.append({
        "account": "",
        "account_name": _("Expenses"),
        "root_type": "",
        "balance": "",
        "indent": 0,
    })
    
    total_expenses = 0
    for account in expense_accounts:
        data.append({
            "account": account.name,
            "account_name": account.account_name,
            "root_type": "Expense",
            "balance": flt(account.balance, 2),
            "indent": 1,
        })
        total_expenses += account.balance
    
    data.append({
        "account": "",
        "account_name": _("Total Expenses"),
        "root_type": "",
        "balance": flt(total_expenses, 2),
        "indent": 0,
    })
    
    # Net Profit/Loss
    net_profit = total_income - total_expenses
    data.append({
        "account": "",
        "account_name": _("Net Profit/Loss"),
        "root_type": "",
        "balance": flt(net_profit, 2),
        "indent": 0,
    })
    
    return data


def get_accounts_by_type(root_type, from_date, to_date, company=None):
    """Get accounts by root type with balances"""
    filters = {
        "root_type": root_type,
        "is_group": 0,
    }
    
    if company:
        filters["company"] = company
    
    accounts = frappe.get_all(
        "Account",
        filters=filters,
        fields=["name", "account_name"]
    )
    
    result = []
    for account in accounts:
        balance = get_account_balance(account.name, from_date, to_date)
        if balance != 0:
            result.append({
                "name": account.name,
                "account_name": account.account_name,
                "balance": abs(balance)  # Show as positive
            })
    
    return result


def get_account_balance(account, from_date, to_date):
    """Calculate account balance for period"""
    gl_entries = frappe.get_all(
        "GL Entry",
        filters={
            "account": account,
            "posting_date": ["between", [from_date, to_date]],
            "is_cancelled": 0,
        },
        fields=["debit", "credit"]
    )
    
    total_debit = sum(flt(entry.debit) for entry in gl_entries)
    total_credit = sum(flt(entry.credit) for entry in gl_entries)
    
    return total_debit - total_credit


def get_chart_data(data):
    """Generate chart data for profit and loss"""
    total_income = 0
    total_expenses = 0
    
    for row in data:
        if row.get("account_name") == "Total Income":
            total_income = row.get("balance", 0)
        elif row.get("account_name") == "Total Expenses":
            total_expenses = row.get("balance", 0)
    
    net_profit = total_income - total_expenses
    
    return {
        "data": {
            "labels": ["Income", "Expenses", "Net Profit"],
            "datasets": [
                {
                    "name": "Amount",
                    "values": [total_income, total_expenses, net_profit]
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


@frappe.whitelist()
def get_profit_and_loss(from_date=None, to_date=None, company=None):
    """API endpoint for profit and loss"""
    filters = {}
    if from_date:
        filters["from_date"] = from_date
    if to_date:
        filters["to_date"] = to_date
    if company:
        filters["company"] = company
    
    columns, data, _, chart = execute(filters)
    return {"columns": columns, "data": data, "chart": chart}
