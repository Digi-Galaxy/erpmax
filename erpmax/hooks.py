# -*- coding: utf-8 -*-
"""
ERPMax - Standalone ERP Application
Built on Frappe Framework
"""

from . import __version__ as app_version

app_name = "erpmax"
app_title = "ERPMax"
app_publisher = "ERPMax"
app_description = "Standalone configurable ERP platform for small to enterprise businesses"
app_email = "support@erpmax.com"
app_license = "MIT"

# Required Apps
required_apps = ["frappe"]

# DocTypes
doctype_js = {
    "Company": "public/js/company.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "Journal Entry": "public/js/journal_entry.js",
    "Payment Entry": "public/js/payment_entry.js",
}

doctype_list_js = {
    "Company": "public/js/company_list.js",
    "Sales Invoice": "public/js/sales_invoice_list.js",
}

doctype_tree_js = {
    "Account": "public/js/account_tree.js",
    "Company": "public/js/company_tree.js",
    "Item Category": "public/js/item_category_tree.js",
}

# Calendar
calendars = ["Holiday List"]

# Scheduled Jobs
scheduler_events = {
    "daily": [
        "erpmax.accounting.doctype.fiscal_year.fiscal_year.auto_create_fiscal_year",
        "erpmax.sales.doctype.recurring_invoice_template.recurring_invoice_template.process_recurring_invoices",
    ],
    "cron": {
        "0 0 * * *": [
            "erpmax.e_invoicing.doctype.zatca_csid.zatca_csid.renew_csid_if_needed",
        ]
    }
}

# Fixtures
fixtures = [
    {
        "dt": "DocType",
        "filters": [["module", "in", ["ERPMax", "Accounts", "Sales", "Purchase", "Inventory", "Commerce"]]]
    },
    {
        "dt": "Role",
        "filters": [["name", "in", ["Company Admin", "Accounts Manager", "Accounts User", "Sales User", "Purchase User"]]]
    },
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["Sales Invoice", "Purchase Invoice", "Journal Entry", "Payment Entry"]]]
    },
]

# Permission Query Conditions
permission_query_conditions = {
    "Company": "erpmax.erpmax.doctype.company.company.get_permission_query_conditions",
}

# Has Permission
has_permission = {
    "Company": "erpmax.erpmax.doctype.company.company.has_permission",
}

# Jinja Filters
jinja = {
    "methods": [
        "erpmax.utils.naming.get_transaction_naming_series",
        "erpmax.accounting.api.reports.get_account_balance",
    ]
}

# Website Routes
website_route_rules = [
    {"from_route": "/erpmax/<path:app_path>", "to_route": "erpmax"},
]

# After Install
after_install = "erpmax.setup.install.after_install"

# After Migrate
after_migrate = "erpmax.setup.migrate.after_migrate"

# On Login
on_login = "erpmax.utils.user.on_login"

# User Data Privacy
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

# Standard Portlets
standard_portlets = {
    "Accounts": [
        {
            "label": "Financial Summary",
            "route": "/app/financial-summary",
            "icon": "fa fa-chart-line",
        }
    ]
}

# Default Roles
default_roles = [
    {"role": "Company Admin", "desk_access": 1},
    {"role": "Accounts Manager", "desk_access": 1},
    {"role": "Accounts User", "desk_access": 1},
    {"role": "Sales User", "desk_access": 1},
    {"role": "Purchase User", "desk_access": 1},
]

# Translations
app_include_js = "/assets/erpmax/js/erpmax.bundle.js?v=2"
app_include_css = "/assets/erpmax/css/erpmax.bundle.css?v=2"

# Global Search
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

# Notification Configuration
notification_config = "erpmax.notifications.get_notification_config"

# Email Hooks
email_hooks = {
    "Sales Invoice": "erpmax.sales.doctype.sales_invoice.sales_invoice.send_invoice_email",
}

# Document Events
doc_events = {
    "Company": {
        "onload": "erpmax.erpmax.doctype.company.company.onload",
        "validate": "erpmax.erpmax.doctype.company.company.validate",
        "on_update": "erpmax.erpmax.doctype.company.company.on_update",
    },
}

# Boot Session
boot_session = "erpmax.boot.boot_session"

# Whitelisted Methods
whitelisted_methods = {
    "erpmax.accounting.api.coa.get_chart_of_accounts": True,
    "erpmax.accounting.api.coa.import_chart_of_accounts": True,
    "erpmax.accounting.api.fiscal_years.get_fiscal_year": True,
    "erpmax.accounting.api.reports.get_trial_balance": True,
    "erpmax.accounting.api.reports.get_balance_sheet": True,
    "erpmax.accounting.api.reports.get_profit_and_loss": True,
    "erpmax.utils.naming.get_naming_series_options": True,
}

# Ignore Links on Cancel
ignore_links_on_delete = [
    "GL Entry",
    "Payment Entry Reference",
]

# Override Whitelisted Methods
override_whitelisted_methods = {
    "frappe.client.get_count": "erpmax.utils.client.get_count",
}

# Tree Doctypes
treeviews = [
    "Account",
    "Company",
    "Item Category",
]

# Before Tests
before_tests = "erpmax.utils.test_utils.before_tests"

# Automatically Cancelled Documents
auto_cancel_exempted_doctypes = [
    "GL Entry",
]

# Accounting Dimensions
accounting_dimension_doctypes = [
    "GL Entry",
    "Sales Invoice",
    "Purchase Invoice",
    "Journal Entry Account",
    "Payment Entry",
]

# Reports
standard_reports = {
    "Trial Balance": "erpmax.accounting.report.trial_balance.trial_balance",
    "General Ledger": "erpmax.accounting.report.general_ledger.general_ledger",
    "Balance Sheet": "erpmax.accounting.report.balance_sheet.balance_sheet",
    "Profit and Loss Statement": "erpmax.accounting.report.profit_and_loss_statement.profit_and_loss_statement",
    "Sales Register": "erpmax.sales.report.sales_register.sales_register",
    "Purchase Register": "erpmax.purchase.report.purchase_register.purchase_register",
    "Accounts Receivable": "erpmax.accounting.report.accounts_receivable.accounts_receivable",
    "Accounts Payable": "erpmax.accounting.report.accounts_payable.accounts_payable",
}

# Setup Wizard
setup_wizard_requires = "/assets/erpmax/js/setup_wizard.js"
setup_wizard_complete = "erpmax.setup.setup_wizard.setup_complete"
setup_wizard_stages = "erpmax.setup.setup_wizard.get_setup_stages"

# Branding
app_logo_url = "/assets/erpmax/images/erpmax-logo.svg?v=2"
app_home = "/app/company"

# Default Language
default_language = "en"