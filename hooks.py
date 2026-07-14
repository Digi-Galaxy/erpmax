# Active hooks
from . import __version__ as app_version

required_apps = ["frappe"]

add_to_apps_screen = [
    {
        "name": "erpmax",
        "logo": "/assets/erpmax/logo.png",
        "title": "Erpmax",
        "route": "/erpmax",
        "has_permission": "erpmax.api.permission.has_app_permission",
    }
]

app_include_css = [
    "/assets/erpmax/css/charts.css",
    "/assets/erpmax/css/fonts.css",
]

app_include_js = [
    "/assets/erpmax/js/charts.js",
    "/assets/erpmax/js/report_engine.js",
    "/assets/erpmax/js/geo_fields.js?v=20260714_6",
]

web_include_css = "/assets/erpmax/css/erpmax.css"
web_include_js = "/assets/erpmax/js/erpmax.js"

page_js = {
    "erpmax-dashboard": "accounting/page/erpmax_dashboard/erpmax_dashboard.js",
}

doctype_js = {
    "Address": "public/js/address.js",
}

doctype_list_js = {
    "Address": "public/js/address_list.js",
    "Customer": "public/js/customer_list.js",
}

override_doctype_class = {
    "Address": "erpmax.overrides.address.CustomAddress",
    "Contact": "erpmax.overrides.contact.CustomContact",
}

jinja = {
    "methods": [
        "erpmax.utils.naming.get_transaction_naming_series",
    ]
}

after_install = "erpmax.setup.install.after_install"
after_migrate = "erpmax.setup.migrate.after_migrate"
notification_config = "erpmax.notifications.get_notification_config"

permission_query_conditions = {
    "Company": "erpmax.organization.doctype.company.company.get_permission_query_conditions",
}

has_permission = {
    "Company": "erpmax.organization.doctype.company.company.has_permission",
}

doc_events = {
    "Branch": {
        "after_insert": "erpmax.overrides.address.after_insert",
        "on_update": "erpmax.overrides.address.on_update",
    },
    "Staff": {
        "after_insert": "erpmax.overrides.address.after_insert",
        "on_update": "erpmax.overrides.address.on_update",
    },
    "Customer": {
        "after_insert": "erpmax.overrides.address.after_insert",
        "on_update": "erpmax.overrides.address.on_update",
    },
    "Supplier": {
        "after_insert": "erpmax.overrides.address.after_insert",
        "on_update": "erpmax.overrides.address.on_update",
    },
    "Bank": {
        "after_insert": "erpmax.overrides.address.after_insert",
        "on_update": "erpmax.overrides.address.on_update",
    },
    "Sales Invoice": {
        "on_submit": "erpmax.taxation.integrations.on_sales_invoice_submit",
        "on_cancel": "erpmax.taxation.integrations.on_sales_invoice_cancel",
    },
    "GL Entry": {
        "after_insert": "erpmax.accounting.realtime.gl_entry.collect_gl_entry",
    },
}

override_whitelisted_methods = {
    "frappe.client.get_count": "erpmax.utils.client.get_count",
    "frappe.desk.query_report.run": "erpmax.utils.client.run_query_report",
}

auto_cancel_exempted_doctypes = ["GL Entry"]
ignore_links_on_delete = ["GL Entry", "Payment Entry Reference"]

scheduler_events = {
    "all": ["erpmax.taxation.services.queue_service.process_queue"],
    "hourly": ["erpmax.taxation.services.queue_service.retry_stuck_queue"],
    "daily": [
        "erpmax.sales.doctype.recurring_invoice_template.recurring_invoice_template.process_recurring_invoices",
        "erpmax.banking.doctype.bank_connection.bank_connection.sync_all_connected_banks",
        "erpmax.service_management.utils.auto_invoice.process_all_auto_invoices",
        "erpmax.taxation.services.queue_service.cleanup_queue",
    ],
}

calendars = ["Holiday List"]

default_roles = [
    {"role": "Company Admin", "desk_access": 1},
    {"role": "Accounts Manager", "desk_access": 1},
    {"role": "Accounts User", "desk_access": 1},
    {"role": "Sales User", "desk_access": 1},
    {"role": "Purchase User", "desk_access": 1},
]

treeviews = ["Account", "Company", "Item Category"]

website_route_rules = [
    {"from_route": "/erpmax/<path:app_path>", "to_route": "erpmax"},
]

global_search_doctypes = {
    "Default": [
        {"doctype": "Company", "index": 0},
        {"doctype": "Customer", "index": 1},
        {"doctype": "Supplier", "index": 2},
        {"doctype": "Item", "index": 3},
        {"doctype": "Sales Invoice", "index": 4},
        {"doctype": "Purchase Invoice", "index": 5},
        {"doctype": "Project", "index": 6},
    ]
}

accounting_dimension_doctypes = [
    "GL Entry",
    "Sales Invoice",
    "Purchase Invoice",
    "Journal Entry Account",
    "Payment Entry",
]

pdf_generator = ["erpmax.utils.pdf.get_chrome_pdf"]
pdf_header_html = ["frappe.utils.pdf.pdf_header_html"]
pdf_footer_html = ["frappe.utils.pdf.pdf_footer_html"]

user_data_fields = [
    {
        "doctype": "Company",
        "match_field": "owner",
        "personal_fields": ["owner_email", "owner_mobile"],
    },
    {
        "doctype": "Customer",
        "match_field": "owner",
    },
]

app_logo_url = "/assets/erpmax/images/erpmax-logo.svg?v=2"
app_home = "/app/control-room"
default_language = "en"

# Active reference copy
# --------------------
# required_apps = ["frappe"]
# add_to_apps_screen = [
# 	{
# 		"name": "erpmax",
# 		"logo": "/assets/erpmax/logo.png",
# 		"title": "Erpmax",
# 		"route": "/erpmax",
# 		"has_permission": "erpmax.api.permission.has_app_permission",
# 	}
# ]
# app_include_css = ["/assets/erpmax/css/charts.css", "/assets/erpmax/css/fonts.css"]
# app_include_js = ["/assets/erpmax/js/charts.js", "/assets/erpmax/js/report_engine.js", "/assets/erpmax/js/geo_fields.js?v=20260714_6"]
# web_include_css = "/assets/erpmax/css/erpmax.css"
# web_include_js = "/assets/erpmax/js/erpmax.js"
# page_js = {"erpmax-dashboard": "accounting/page/erpmax_dashboard/erpmax_dashboard.js"}
# doctype_js = {"Address": "public/js/address.js"}
# doctype_list_js = {"Address": "public/js/address_list.js", "Customer": "public/js/customer_list.js"}
# override_doctype_class = {"Address": "erpmax.overrides.address.CustomAddress", "Contact": "erpmax.overrides.contact.CustomContact"}
# jinja = {"methods": ["erpmax.utils.naming.get_transaction_naming_series"]}
# after_install = "erpmax.setup.install.after_install"
# after_migrate = "erpmax.setup.migrate.after_migrate"
# notification_config = "erpmax.notifications.get_notification_config"
# permission_query_conditions = {"Company": "erpmax.organization.doctype.company.company.get_permission_query_conditions"}
# has_permission = {"Company": "erpmax.organization.doctype.company.company.has_permission"}
# doc_events = {
# 	"Branch": {"after_insert": "erpmax.overrides.address.after_insert", "on_update": "erpmax.overrides.address.on_update"},
# 	"Staff": {"after_insert": "erpmax.overrides.address.after_insert", "on_update": "erpmax.overrides.address.on_update"},
# 	"Customer": {"after_insert": "erpmax.overrides.address.after_insert", "on_update": "erpmax.overrides.address.on_update"},
# 	"Supplier": {"after_insert": "erpmax.overrides.address.after_insert", "on_update": "erpmax.overrides.address.on_update"},
# 	"Bank": {"after_insert": "erpmax.overrides.address.after_insert", "on_update": "erpmax.overrides.address.on_update"},
# 	"Sales Invoice": {"on_submit": "erpmax.taxation.integrations.on_sales_invoice_submit", "on_cancel": "erpmax.taxation.integrations.on_sales_invoice_cancel"},
# 	"GL Entry": {"after_insert": "erpmax.accounting.realtime.gl_entry.collect_gl_entry"},
# }
# override_whitelisted_methods = {"frappe.client.get_count": "erpmax.utils.client.get_count", "frappe.desk.query_report.run": "erpmax.utils.client.run_query_report"}
# auto_cancel_exempted_doctypes = ["GL Entry"]
# ignore_links_on_delete = ["GL Entry", "Payment Entry Reference"]
# scheduler_events = {"all": ["erpmax.taxation.services.queue_service.process_queue"], "hourly": ["erpmax.taxation.services.queue_service.retry_stuck_queue"], "daily": ["erpmax.sales.doctype.recurring_invoice_template.recurring_invoice_template.process_recurring_invoices", "erpmax.banking.doctype.bank_connection.bank_connection.sync_all_connected_banks", "erpmax.service_management.utils.auto_invoice.process_all_auto_invoices", "erpmax.taxation.services.queue_service.cleanup_queue"]}
# calendars = ["Holiday List"]
# default_roles = [{"role": "Company Admin", "desk_access": 1}, {"role": "Accounts Manager", "desk_access": 1}, {"role": "Accounts User", "desk_access": 1}, {"role": "Sales User", "desk_access": 1}, {"role": "Purchase User", "desk_access": 1}]
# treeviews = ["Account", "Company", "Item Category"]
# website_route_rules = [{"from_route": "/erpmax/<path:app_path>", "to_route": "erpmax"}]
# global_search_doctypes = {"Default": [{"doctype": "Company", "index": 0}, {"doctype": "Customer", "index": 1}, {"doctype": "Supplier", "index": 2}, {"doctype": "Item", "index": 3}, {"doctype": "Sales Invoice", "index": 4}, {"doctype": "Purchase Invoice", "index": 5}, {"doctype": "Project", "index": 6}]}
# accounting_dimension_doctypes = ["GL Entry", "Sales Invoice", "Purchase Invoice", "Journal Entry Account", "Payment Entry"]
# pdf_generator = ["erpmax.utils.pdf.get_chrome_pdf"]
# pdf_header_html = ["frappe.utils.pdf.pdf_header_html"]
# pdf_footer_html = ["frappe.utils.pdf.pdf_footer_html"]
# user_data_fields = [{"doctype": "Company", "match_field": "owner", "personal_fields": ["owner_email", "owner_mobile"]}, {"doctype": "Customer", "match_field": "owner"}]
# app_logo_url = "/assets/erpmax/images/erpmax-logo.svg?v=2"
# app_home = "/app/control-room"
# default_language = "en"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erpmax",
# 		"logo": "/assets/erpmax/logo.png",
# 		"title": "Erpmax",
# 		"route": "/erpmax",
# 		"has_permission": "erpmax.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpmax/css/erpmax.css"
# app_include_js = "/assets/erpmax/js/erpmax.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpmax/css/erpmax.css"
# web_include_js = "/assets/erpmax/js/erpmax.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpmax/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpmax/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpmax.utils.jinja_methods",
# 	"filters": "erpmax.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpmax.install.before_install"
# after_install = "erpmax.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpmax.uninstall.before_uninstall"
# after_uninstall = "erpmax.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpmax.utils.before_app_install"
# after_app_install = "erpmax.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpmax.utils.before_app_uninstall"
# after_app_uninstall = "erpmax.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpmax.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpmax.tasks.all"
# 	],
# 	"daily": [
# 		"erpmax.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpmax.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpmax.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpmax.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpmax.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpmax.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpmax.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpmax.utils.before_request"]
# after_request = ["erpmax.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpmax.utils.before_job"]
# after_job = ["erpmax.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpmax.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
