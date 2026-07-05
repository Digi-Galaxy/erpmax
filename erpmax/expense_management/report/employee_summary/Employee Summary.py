import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = []
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]
    if filters.get("department"):
        cond.append("department=%(department)s")
        params["department"] = filters["department"]

    where = " AND ".join(cond) if cond else "1=1"
    rows = frappe.db.sql("""SELECT name, employee_name, designation, department, status, date_of_joining
       FROM `tabEmployee`
       WHERE {where} ORDER BY department, employee_name""".format(where=where),
        params, as_dict=True)
    data = [{"name": r.name, "employee_name": r.employee_name,
        "designation": r.designation, "department": r.department,
        "status": r.status, "date_of_joining": r.date_of_joining} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "name", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Date of Joining"), "fieldname": "date_of_joining", "fieldtype": "Date", "width": 120},
    ]