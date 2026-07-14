# Company — Module: Organization

## Overview
Company is the central entity of ERPMax. It represents a legal business entity with accounting defaults, tax configuration, feature flags, and multi-branch support.

## Changes Applied (2026-07-14)

### Module Migration
- Moved from `erpmax/erpmax/doctype/company/` (core ERPMax bucket) → `erpmax/organization/doctype/company/`
- Module field in `company.json`: `ERPMax` → `Organization`

### JSON Fixes
- Replaced with backup version (149 fields, stable)
- Removed `default_distributor` and `region` from `field_order` (no field definitions existed)
- Added 4 new fields:
  - `sb_chart_of_accounts` (Section Break — Chart of Accounts)
  - `create_chart_of_accounts_based_on` (Select: Standard Template / Our Templates / Standard with Numbers)
  - `chart_of_accounts_template` (Link → Chart of Accounts Template, visible when "Our Templates" selected)
  - `cb_chart_of_accounts` (Column Break)

### Python Controller (company.py)
- Replaced with backup version (449 lines, extended feature set)
- Fixed import paths for clone structure:
  - `erpmax.accounts.doctype.company_account_setup` → `erpmax.doctype.company_account_setup`
  - `erpmax.utilities.doctype.transaction_deletion_record` → `erpmax.erpmax.doctype.transaction_deletion_record`
- COA features added: `_suggest_coa_template()`, `_handle_coa_creation()`, `_create_chart_of_accounts()`, `_populate_company_accounts()`, `get_permission_query_conditions()`
- COA API: Copied `accounting/api/coa.py` + 10 template JSONs from backup

### JS Files
- `company.js`: Fixed dotted paths → `erpmax.organization.doctype.company.*`
- `company_tree.js`: Fixed dotted paths → `erpmax.organization.doctype.company.*`

### Dependencies
- `Company Account` (child table) — copied from backup to `accounts/doctype/company_account/` (module: Accounts)
- `Chart of Accounts Template` doctype — already exists in `accounting/doctype/`

### Version
- Set to `0.0.01` (from `1.0.0`)

## Related Doctypes (Missing from Clone — to be added module-by-module)
See `~/backup_erpmax/` for source files of:
- Accounts: Budget, Budget Detail, Exchange Rate, Payment Term, Payment Term Detail
- CRM: Lead, Opportunity
- E-Invoicing: Tax Compliance*, ZATCA*
- Geo Intelligence: Geo Field Mapping, Geo Settings
- HRMS: Employee Contract, Holiday List, Timesheet (+Detail)
- Service Management: Site, Contract*, Maintenance*, Stage Log
- Utilities: Email/SMS Template (+Variable), FBR Sale Type, HS Code
