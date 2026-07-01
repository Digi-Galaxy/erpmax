frappe.query_reports["Balance Sheet"]={"filters":[
 {"fieldname":"company","label":__("Company"),"fieldtype":"Link","options":"Company","reqd":1,"default":frappe.defaults.get_user_default("Company")},
 {"fieldname":"as_on_date","label":__("As On Date"),"fieldtype":"Date","reqd":1,"default":frappe.datetime.get_today()}
]};