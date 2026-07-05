# ERPMax Repository Tree

Functional tree from the current source scan. Generated from the working copy, with `__pycache__` and other transient artifacts omitted.

```text
E:\Projects\erpmax
├── AGENTS.md
├── MILESTONES.md
├── PROJECT_DESCRIPTION.md
├── README.md
├── ROADMAP.md
├── SESSION_STATUS.md
├── TASKS.md
├── VISION.md
├── WORKING_UNDERSTANDINGS.md
├── ai
│   ├── agents
│   │   ├── MISTAKES.md
│   │   ├── NOTES.md
│   │   ├── USER_INSTRUCTIONS.md
│   │   ├── agent-knowledge-workflow.md
│   │   └── instructions
│   │       └── erpmax-commercial-terms-features.md
│   ├── knowledge
│   │   └── discoveries.md
│   ├── learning
│   ├── memory
│   │   ├── codebase-scan.md
│   │   └── session-chat.md
│   └── projects
│       └── commission
│           └── NOTES.md
├── docs
│   ├── README.md
│   ├── PROJECT_DESCRIPTION.md
│   ├── ROADMAP.md
│   ├── SESSION_STATUS.md
│   ├── WORKING_UNDERSTANDINGS.md
│   ├── FEATURE_REQUIREMENTS.md
│   ├── audit
│   │   ├── COA_AUDIT.md
│   │   ├── IMPLEMENTATION_NOTES.md
│   │   └── COMPARATIVE_AUDIT.md
│   ├── chat_sessions
│   │   ├── session_2026-07-01.md
│   │   ├── session_summary.md
│   │   ├── session_summary_20260701.md
│   │   └── session_summary_20260705.md
│   ├── planning
│   │   ├── ROADMAP.md
│   │   └── TASKS.md
│   ├── project
│   │   ├── PROJECT_DESCRIPTION.md
│   │   └── WORKING_UNDERSTANDINGS.md
│   ├── requirements
│   │   └── FEATURE_REQUIREMENTS.md
│   └── status
│       ├── CHAT_SESSION_COMPACT.md
│       ├── CHAT_SESSION_SUMMARY_2026-07-05.md
│       ├── CHAT_SESSIONS.md
│       ├── PROJECT_STATE_MATRIX.md
│       ├── SESSION_CHAT_LOG.md
│       └── SESSION_STATUS.md
├── erpmax
│   ├── accounting
│   │   ├── api
│   │   ├── doctype
│   │   │   ├── account
│   │   │   ├── budget
│   │   │   ├── budget_detail
│   │   │   ├── chart_of_accounts_account
│   │   │   ├── chart_of_accounts_template
│   │   │   ├── cost_center
│   │   │   ├── exchange_rate
│   │   │   ├── fiscal_year
│   │   │   ├── gl_entry
│   │   │   ├── holiday_list
│   │   │   ├── internal_account_transaction
│   │   │   ├── journal_entry
│   │   │   ├── journal_entry_account
│   │   │   ├── partner_account
│   │   │   ├── partner_transaction
│   │   │   ├── payment_entry
│   │   │   ├── payment_entry_reference
│   │   │   ├── payment_term
│   │   │   ├── payment_term_detail
│   │   │   ├── purchase_taxes_and_charges
│   │   │   ├── purchase_taxes_and_charges_template
│   │   │   ├── sales_taxes_and_charges
│   │   │   └── sales_taxes_and_charges_template
│   │   ├── page
│   │   │   └── erpmax_dashboard
│   │   ├── realtime
│   │   └── report
│   │       ├── accounts_payable
│   │       ├── accounts_receivable
│   │       ├── balance_sheet
│   │       ├── customer_statement
│   │       ├── customer_summary
│   │       ├── general_ledger
│   │       ├── profit_and_loss_statement
│   │       ├── supplier_statement
│   │       ├── supplier_summary
│   │       ├── tax_summary
│   │       └── trial_balance
│   ├── banking
│   │   ├── docs
│   │   ├── doctype
│   │   │   ├── bank_account
│   │   │   ├── bank_connection
│   │   │   ├── bank_reconciliation
│   │   │   ├── bank_reconciliation_item
│   │   │   ├── bank_statement
│   │   │   ├── bank_statement_line
│   │   │   ├── bank_transaction
│   │   │   └── reconciliation_rule
│   │   └── report
│   │       ├── bank_account_summary
│   │       └── cash_and_bank_balances
│   ├── business_setup
│   │   └── doctype
│   │       ├── distributor
│   │       ├── distributor_commission
│   │       └── region
│   ├── commerce
│   │   └── doctype
│   │       ├── address
│   │       ├── address_link
│   │       ├── customer
│   │       ├── lead
│   │       ├── opportunity
│   │       ├── vat_process
│   │       └── vat_process_item
│   ├── e_invoicing
│   │   └── doctype
│   │       ├── zatca_csid
│   │       └── zatca_csr_settings
│   ├── erpmax
│   │   ├── doctype
│   │   │   ├── activity_log
│   │   │   ├── company
│   │   │   ├── company_account_setup
│   │   │   ├── company_configuration_row
│   │   │   ├── company_industry
│   │   │   ├── company_user
│   │   │   ├── country_compliance
│   │   │   ├── customer_addon_settings
│   │   │   ├── email_template
│   │   │   ├── email_template_variable
│   │   │   ├── erpmax_settings
│   │   │   ├── holiday_list
│   │   │   ├── internal_account_transaction
│   │   │   ├── partner_account
│   │   │   ├── partner_transaction
│   │   │   ├── party
│   │   │   ├── party_account
│   │   │   ├── party_type
│   │   │   ├── purchase_taxes_and_charges
│   │   │   ├── purchase_taxes_and_charges_template
│   │   │   ├── sales_invoice_addon_settings
│   │   │   ├── sales_taxes_and_charges
│   │   │   ├── sales_taxes_and_charges_template
│   │   │   ├── sms_template
│   │   │   ├── sms_template_variable
│   │   │   ├── timesheet
│   │   │   ├── timesheet_detail
│   │   │   └── transaction_deletion_record
│   │   ├── page
│   │   │   ├── control_room
│   │   │   ├── report_builder
│   │   │   └── settings_page
│   │   └── setup
│   ├── expense_management
│   │   └── doctype
│   │       ├── expense_claim
│   │       ├── expense_claim_detail
│   │       └── expense_type
│   ├── inventory
│   │   └── doctype
│   │       ├── item
│   │       ├── item_category
│   │       ├── item_price
│   │       ├── price_list
│   │       └── pricing_rule
│   ├── printings
│   │   └── doctype
│   │       └── pdf_settings
│   ├── project_management
│   │   ├── doctype
│   │   │   ├── project
│   │   │   └── project_service
│   │   └── report
│   │       └── project_profitability
│   ├── purchase
│   │   ├── doctype
│   │   │   ├── debit_note
│   │   │   ├── debit_note_item
│   │   │   ├── debit_note_tax
│   │   │   ├── purchase_invoice
│   │   │   ├── purchase_invoice_item
│   │   │   ├── purchase_invoice_tax
│   │   │   ├── purchase_order
│   │   │   ├── purchase_order_item
│   │   │   ├── purchase_order_tax
│   │   │   ├── supplier
│   │   │   ├── supplier_quotation
│   │   │   ├── supplier_quotation_item
│   │   │   └── supplier_quotation_tax
│   │   └── report
│   │       └── purchase_register
│   ├── reporting
│   │   └── doctype
│   │       ├── reporting_standard
│   │       └── reporting_standard_account
│   ├── sales
│   │   ├── doctype
│   │   │   ├── credit_note
│   │   │   ├── credit_note_item
│   │   │   ├── credit_note_tax
│   │   │   ├── delivery_note
│   │   │   ├── delivery_note_item
│   │   │   ├── proforma_invoice
│   │   │   ├── quotation
│   │   │   ├── quotation_item
│   │   │   ├── quotation_tax
│   │   │   ├── recurring_invoice_item
│   │   │   ├── recurring_invoice_template
│   │   │   ├── sales_invoice
│   │   │   ├── sales_invoice_item
│   │   │   ├── sales_invoice_tax
│   │   │   ├── sales_order
│   │   │   ├── sales_order_item
│   │   │   ├── sales_order_tax
│   │   │   ├── transport_delivery
│   │   │   └── transport_delivery_item
│   │   └── report
│   │       ├── item_wise_sales
│   │       ├── sales_by_customer
│   │       ├── sales_by_item_category
│   │       ├── sales_invoice_totals
│   │       ├── sales_invoice_totals_by_customer
│   │       ├── sales_invoice_totals_by_item
│   │       └── sales_register
│   ├── setup
│   └── stock
│       └── doctype
│           ├── stock_entry
│           ├── stock_entry_item
│           ├── stock_ledger_entry
│           └── warehouse
├── fixing
├── go-services
│   ├── internal
│   │   ├── api
│   │   ├── cache
│   │   ├── config
│   │   ├── services
│   │   └── worker
│   └── main.go
└── modules.txt
```

## Note
- `Taxation` appears in the module list, but there is no dedicated `erpmax/taxation/` source folder in the current scan.
