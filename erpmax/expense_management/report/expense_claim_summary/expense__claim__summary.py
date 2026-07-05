import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("employee"):
        cond.append("employee=%(employee)s")
        params["employee"] = filters["employee"]
    if filters.get("from_date") and filters.get("to_date"):
        cond.append("posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({"from_date": filters["from_date"], "to_date": filters["to_date"]})

    rows = frappe.db.sql("""SELECT employee, employee_name, expense_type,
              SUM(total_claimed_amount) AS claimed,
              SUM(total_sanctioned_amount) AS sanctioned
       FROM `tabExpense Claim`
       WHERE {cond} GROUP BY employee, employee_name, expense_type ORDER BY employee, expense_type""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"employee": r.employee, "employee_name": r.employee_name,
        "expense_type": r.expense_type, "claimed": r.claimed or 0,
        "sanctioned": r.sanctioned or 0} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": _("Expense Type"), "fieldname": "expense_type", "fieldtype": "Link", "options": "Expense Type", "width": 180},
        {"label": _("Claimed"), "fieldname": "claimed", "fieldtype": "Currency", "width": 130},
        {"label": _("Sanctioned"), "fieldname": "sanctioned", "fieldtype": "Currency", "width": 130},
    ]