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

required_apps = ["frappe"]

# doctype_js - Not needed, Frappe auto-loads JS from doctype directories

doctype_tree_js = {
    "Account": "public/js/account_tree.js",
    "Company": "public/js/company_tree.js",
    "Item Category": "public/js/item_category_tree.js",
}

calendars = ["Holiday List"]

scheduler_events = {
    "daily": [
        "erpmax.accounting.doctype.fiscal_year.fiscal_year.auto_create_fiscal_year",
        "erpmax.sales.doctype.recurring_invoice_template.recurring_invoice_template.process_recurring_invoices",
        "erpmax.banking.doctype.bank_connection.bank_connection.sync_all_connected_banks",
    ],
    "cron": {
        "0 0 * * *": [
            "erpmax.taxation.doctype.zatca_csid.zatca_csid.renew_csid_if_needed",
        ]
    }
}

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
        "filters": [["document_type", "in", ["Sales Invoice", "Purchase Invoice", "Journal Entry", "Payment Entry", "Expense Claim"]]]
    },
]

permission_query_conditions = {
    "Company": "erpmax.erpmax.doctype.company.company.get_permission_query_conditions",
}

has_permission = {
    "Company": "erpmax.erpmax.doctype.company.company.has_permission",
}

jinja = {
    "methods": [
        "erpmax.utils.naming.get_transaction_naming_series",
        "erpmax.accounting.api.reports.get_account_balance",
    ]
}

website_route_rules = [
    {"from_route": "/erpmax/<path:app_path>", "to_route": "erpmax"},
]

after_install = "erpmax.setup.install.after_install"
after_migrate = "erpmax.setup.migrate.after_migrate"
on_login = "erpmax.utils.user.on_login"

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

default_roles = [
    {"role": "Company Admin", "desk_access": 1},
    {"role": "Accounts Manager", "desk_access": 1},
    {"role": "Accounts User", "desk_access": 1},
    {"role": "Sales User", "desk_access": 1},
    {"role": "Purchase User", "desk_access": 1},
]

app_include_js = [
    "/assets/erpmax/js/erpmax.bundle.js?v=2",
    "/assets/erpmax/js/pdf_generator.js",
    "/assets/erpmax/js/feature_toggle.js",
]
app_include_css = "/assets/erpmax/css/erpmax.bundle.css?v=2"

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

notification_config = "erpmax.notifications.get_notification_config"

doc_events = {
    "Company": {
        "onload": "erpmax.erpmax.doctype.company.company.onload",
        "validate": "erpmax.erpmax.doctype.company.company.validate",
        "on_update": "erpmax.erpmax.doctype.company.company.on_update",
    },
    "GL Entry": {
        "after_insert": "erpmax.accounting.realtime.gl_entry.collect_gl_entry",
    },
    "*": {
    },
    "Sales Invoice": {
        "validate": "erpmax.commercial_terms.hooks.sales_invoice_validate",
        "on_submit": "erpmax.commercial_terms.hooks.sales_invoice_on_submit",
        "on_cancel": "erpmax.commercial_terms.hooks.sales_invoice_on_cancel",
    },
    "Purchase Invoice": {
        "validate": "erpmax.commercial_terms.hooks.purchase_invoice_validate",
        "on_submit": "erpmax.commercial_terms.hooks.purchase_invoice_on_submit",
        "on_cancel": "erpmax.commercial_terms.hooks.purchase_invoice_on_cancel",
    },
}

page_js = {"erpmax-dashboard": "erpmax.accounting.page.erpmax_dashboard.erpmax_dashboard.js"}
boot_session = "erpmax.boot.boot_session"

whitelisted_methods = {
    "erpmax.accounting.api.coa.get_chart_of_accounts": True,
    "erpmax.accounting.api.coa.import_chart_of_accounts": True,
    "erpmax.accounting.api.fiscal_years.get_fiscal_year": True,
    "erpmax.accounting.api.reports.trial_balance": True,
    "erpmax.accounting.api.reports.balance_sheet": True,
    "erpmax.accounting.api.reports.profit_and_loss": True,
    "erpmax.utils.naming.get_naming_series_options": True,
    "erpmax.banking.report.bank_account_summary.bank_account_summary.get_bank_account_summary": True,
    "erpmax.banking.report.cash_bank_balances.cash_bank_balances.get_cash_bank_balances": True,
    "erpmax.utils.fuzzy_matching.test_fuzzy_match": True,
    "erpmax.utils.fuzzy_matching.get_matching_suggestions": True,
    "erpmax.utils.feature_toggle.get_feature_toggles": True,
    "erpmax.banking.doctype.bank_transaction.auto_reconcile.auto_reconcile_statement": True,
    "erpmax.banking.doctype.bank_transaction.auto_reconcile.auto_reconcile_single": True,
    "erpmax.erpmax.page.control_room.control_room.get_realtime_data": True,
    "erpmax.erpmax.page.control_room.control_room.refresh_dashboard": True,
    "erpmax.erpmax.page.report_builder.report_builder.generate_report": True,
    "erpmax.erpmax.page.settings_page.settings_page.get_system_info": True,
    "erpmax.erpmax.page.settings_page.settings_page.get_module_status": True,
    "erpmax.erpmax.page.settings_page.settings_page.clear_cache": True,
}

ignore_links_on_delete = ["GL Entry", "Payment Entry Reference"]

override_whitelisted_methods = {
    "frappe.client.get_count": "erpmax.utils.client.get_count",
}

treeviews = ["Account", "Company", "Item Category"]
before_tests = "erpmax.utils.test_utils.before_tests"
auto_cancel_exempted_doctypes = ["GL Entry"]

accounting_dimension_doctypes = [
    "GL Entry", "Sales Invoice", "Purchase Invoice", "Journal Entry Account", "Payment Entry",
]

standard_reports = {
    "Trial Balance": "erpmax.accounting.report.trial_balance.trial_balance",
    "General Ledger": "erpmax.accounting.report.general_ledger.general_ledger",
    "Balance Sheet": "erpmax.accounting.report.balance_sheet.balance_sheet",
    "Profit and Loss Statement": "erpmax.accounting.report.profit_and_loss.profit_and_loss",
    "Accounts Receivable": "erpmax.accounting.report.aged_receivables.aged_receivables",
    "Accounts Payable": "erpmax.accounting.report.aged_payables.aged_payables",
    "Customer Summary": "erpmax.accounting.report.customer_summary.customer_summary",
    "Supplier Summary": "erpmax.accounting.report.supplier_summary.supplier_summary",
    "Customer Statement": "erpmax.accounting.report.customer_statements.customer_statements",
    "Supplier Statement": "erpmax.accounting.report.supplier_statements.supplier_statements",
    "Tax Summary": "erpmax.accounting.report.tax_summary.tax_summary",
    "Receipts and Payments": "erpmax.accounting.report.receipts_and_payments.receipts_and_payments",
    "Sales Register": "erpmax.sales.report.sales_register.sales_register",
    "Sales Invoice Totals": "erpmax.sales.report.sales_invoice_totals.sales_invoice_totals",
    "Sales Invoice Totals by Customer": "erpmax.sales.report.sales_invoice_totals_by_customer.sales_invoice_totals_by_customer",
    "Sales Invoice Totals by Item": "erpmax.sales.report.sales_invoice_totals_by_item.sales_invoice_totals_by_item",
    "Item-wise Sales": "erpmax.sales.report.item_wise_sales.item_wise_sales",
    "Sales by Customer": "erpmax.sales.report.sales_by_customer.sales_by_customer",
    "Purchase Register": "erpmax.purchase.report.purchase_register.purchase_register",
    "Bank Account Summary": "erpmax.banking.report.bank_account_summary.bank_account_summary",
    "Cash and Bank Balances": "erpmax.banking.report.cash_bank_balances.cash_bank_balances",
    "Expense Claim Summary": "erpmax.expense_management.report.expense_claim_summary.expense_claim_summary",
    "Employee Summary": "erpmax.expense_management.report.employee_summary.employee_summary",
    "Project Profitability": "erpmax.project_management.report.project_profitability.project_profitability",
    "Income and Expenditure": "erpmax.reporting.report.income_and_expenditure.income_and_expenditure",
}

setup_wizard_requires = "/assets/erpmax/js/setup_wizard.js"
setup_wizard_complete = "erpmax.setup.setup_wizard.setup_complete"
setup_wizard_stages = "erpmax.setup.setup_wizard.get_setup_stages"

app_logo_url = "/assets/erpmax/images/erpmax-logo.svg?v=2"
app_home = "/app/control-room"
default_language = "en"
