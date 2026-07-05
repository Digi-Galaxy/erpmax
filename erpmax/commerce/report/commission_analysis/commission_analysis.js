frappe.query_reports["Commission Analysis"] = {
    "filters": [
        {
            "fieldname": "agent",
            "label": __("Agent"),
            "fieldtype": "Link",
            "options": "Sales Agent",
            "width": 80
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": 80
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": 80
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Accrued", "Paid", "Recovered", "Cancelled"],
            "width": 80
        }
    ]
};
