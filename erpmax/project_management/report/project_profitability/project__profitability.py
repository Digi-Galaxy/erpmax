import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    cond = ["docstatus=1"]
    params = {}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters["company"]

    rows = frappe.db.sql("""SELECT name, project_name,
              expected_start_date, expected_end_date,
              estimated_costs, status
       FROM `tabProject`
       WHERE {cond} ORDER BY name""".format(cond=" AND ".join(cond)),
        params, as_dict=True)
    data = [{"name": r.name, "project_name": r.project_name,
        "start_date": r.expected_start_date, "end_date": r.expected_end_date,
        "estimated_costs": r.estimated_costs or 0, "status": r.status} for r in rows]
    return get_columns(), data

def get_columns():
    return [
        {"label": _("Project"), "fieldname": "name", "fieldtype": "Link", "options": "Project", "width": 180},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 250},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 110},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 110},
        {"label": _("Estimated Cost"), "fieldname": "estimated_costs", "fieldtype": "Currency", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]