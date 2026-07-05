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
    "Company": "erpmax/doctype/company/company.js",
}

doctype_tree_js = {
    "Account": "accounting/doctype/account/account_tree.js",
    "Company": "erpmax/doctype/company/company_tree.js",
    "Item Category": "inventory/doctype/item_category/item_category_tree.js",
}

# Calendar
calendars = ["Holiday List"]

# Scheduled Jobs
scheduler_events = {
    "daily": [
        "erpmax.sales.doctype.recurring_invoice_template.recurring_invoice_template.process_recurring_invoices",
        "erpmax.banking.doctype.bank_connection.bank_connection.sync_all_connected_banks",
    ]
}

# Fixtures
fixtures = [
    {
        "dt": "DocType",
        "filters": [["module", "in", ["ERPMax", "Accounting", "Sales", "Purchase", "Inventory", "Commerce", "Banking", "Expense Management"]]]
    },
    {
        "dt": "Role",
        "filters": [["name", "in", ["Company Admin", "Accounts Manager", "Accounts User", "Sales User", "Purchase User", "Finance Manager", "Sales Manager"]]]
    },
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["Sales Invoice", "Purchase Invoice", "Journal Entry", "Payment Entry", "Expense Claim", "Credit Note", "Debit Note"]]]
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
app_include_js = [
    "/assets/erpmax/js/erpmax.bundle.js",
    "/assets/erpmax/js/charts.js",
    "/assets/erpmax/js/report_engine.js",
]
app_include_css = [
    "/assets/erpmax/css/erpmax.bundle.css",
    "/assets/erpmax/css/charts.css",
]

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

# Document Events
doc_events = {
    "GL Entry": {
        "after_insert": "erpmax.accounting.realtime.gl_entry.collect_gl_entry",
    },
    # Activity logging hooks
    "*": {
        "on_update": "erpmax.erpmax.doctype.activity_log.activity_log.on_document_update",
        "after_insert": "erpmax.erpmax.doctype.activity_log.activity_log.on_document_create",
        "on_trash": "erpmax.erpmax.doctype.activity_log.activity_log.on_document_delete",
    },
}

# Page JS
page_js = {"erpmax-dashboard": "accounting/page/erpmax_dashboard/erpmax_dashboard.js"}

# Whitelisted Methods
whitelisted_methods = {
    "erpmax.accounting.api.coa.get_chart_of_accounts": True,
    "erpmax.accounting.api.coa.import_chart_of_accounts": True,
    "erpmax.accounting.api.fiscal_years.get_fiscal_year": True,
    "erpmax.accounting.api.reports.trial_balance": True,
    "erpmax.accounting.api.reports.balance_sheet": True,
    "erpmax.accounting.api.reports.profit_and_loss": True,
    "erpmax.utils.naming.get_naming_series_options": True,
    # Banking reports
    "erpmax.banking.report.bank_account_summary.bank_account_summary.get_bank_account_summary": True,
    "erpmax.banking.report.cash_and_bank_balances.cash_and_bank_balances.get_cash_and_bank_balances": True,
    # Fuzzy matching
    "erpmax.utils.fuzzy_matching.test_fuzzy_match": True,
    "erpmax.utils.fuzzy_matching.get_matching_suggestions": True,
    # Auto reconciliation
    "erpmax.banking.doctype.bank_transaction.auto_reconcile.auto_reconcile_statement": True,
    "erpmax.banking.doctype.bank_transaction.auto_reconcile.auto_reconcile_single": True,
}

# Ignore Links on Cancel
ignore_links_on_delete = [
    "GL Entry",
    "Payment Entry Reference",
]

# Override Whitelisted Methods
override_whitelisted_methods = {
	"frappe.client.get_count": "erpmax.utils.client.get_count",
	"frappe.desk.query_report.run": "erpmax.utils.client.run_query_report",
}

# Tree Doctypes
treeviews = [
    "Account",
    "Company",
    "Item Category",
]

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
    # Core Accounting Reports
    "Trial Balance": "erpmax.accounting.report.trial_balance.trial_balance",
    "General Ledger": "erpmax.accounting.report.general_ledger.general_ledger",
    "Balance Sheet": "erpmax.accounting.report.balance_sheet.balance_sheet",
    "Profit and Loss Statement": "erpmax.accounting.report.profit_and_loss_statement.profit_and_loss_statement",
    "Accounts Receivable": "erpmax.accounting.report.accounts_receivable.accounts_receivable",
    "Accounts Payable": "erpmax.accounting.report.accounts_payable.accounts_payable",
    
    # Customer/Supplier Reports
    "Customer Summary": "erpmax.accounting.report.customer_summary.customer_summary",
    "Supplier Summary": "erpmax.accounting.report.supplier_summary.supplier_summary",
    "Customer Statement": "erpmax.accounting.report.customer_statement.customer_statement",
    "Supplier Statement": "erpmax.accounting.report.supplier_statement.supplier_statement",
    
    # Tax Reports
    "Tax Summary": "erpmax.accounting.report.tax_summary.tax_summary",
    
    # Sales Reports
    "Sales Register": "erpmax.sales.report.sales_register.sales_register",
    "Item-wise Sales": "erpmax.sales.report.item_wise_sales.item_wise_sales",
    "Sales by Customer": "erpmax.sales.report.sales_by_customer.sales_by_customer",
    "Sales by Item Category": "erpmax.sales.report.sales_by_item_category.sales_by_item_category",
    
    # Purchase Reports
    "Purchase Register": "erpmax.purchase.report.purchase_register.purchase_register",
    
    # Banking Reports
    "Bank Account Summary": "erpmax.banking.report.bank_account_summary.bank_account_summary",
    "Cash and Bank Balances": "erpmax.banking.report.cash_and_bank_balances.cash_and_bank_balances",
    
    # Project Reports
    "Project Profitability": "erpmax.project_management.report.project_profitability.project_profitability",
}

# Branding
app_logo_url = "/assets/erpmax/images/erpmax-logo.svg?v=2"
app_home = "/app/control-room"

# Default Language
default_language = "en"

