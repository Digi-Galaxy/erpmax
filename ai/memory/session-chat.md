# ERPMax — Session Chat Log

## 2026-07-05 — Standalone Reset + Core Doctypes

### Summary
- Rewrote `E:\Projects\erpmax\docs\` to match the current standalone ERPMax baseline.
- Recreated the `erpmax` app with `bench new-app`, pushed it to `Digi-Galaxy/erpmax`, and created `erpmax.celtcoksa.com`.
- Created and migrated the core doctypes: `Company`, `Customer`, `Item`, `Account`, `Fiscal Year`, `Address`, `Sales Invoice`, `VAT Process`, plus child tables.

### Current State
- ERPMax is still standalone Frappe v15.
- The repo is on `Digi-Galaxy/erpmax` `develop`.
- The live site is `erpmax.celtcoksa.com` with `frappe` + `erpmax` only.
- ZATCA has not been imported into the standalone build yet.
- COA templates, transport, reporting, reconciliation, portal, assets, expenses, and budget work remain open.

### Next Steps
1. Import ZATCA into ERPMax as a module.
2. Build the COA template system.
3. Verify company-linked COA runtime generation.
4. Continue the transactional workflow and reporting backlog.

## 2025-07-05 — Commission Phase 2 (Hierarchy + GL Fixes)

### Summary
- **Sales Agent doctype** created (agent_name, agent_type, parent_agent, commission_rate, territory, default_commission_account)
- **Customer doctype** updated: added `default_sales_agent` field
- **CT Template doctype** updated: split_method (Hierarchy/Percentage/Rule Based), head_office_pct, field_pct, territory, customer_group
- **evaluator.py** updated: resolve_agent_hierarchy(), split_commission_hierarchy(), split_commission_percentage(), _find_parent/ensure_account fixes
- **hooks.py**: resolve_templates() passes template-level commission fields to rules
- **get_gl_entries_for_term()**: Commission effect uses agent's default_commission_account for credit side
- Region renamed to Territory on Sales Agent doctype

### Architecture Decisions
- Commission GL: Dr Commission Expense / Cr agent's default_commission_account (Payable)
- Split "Hierarchy" = proportional to each agent's commission_rate
- Split "Percentage" = head_office_pct% to head agents, field_pct% split by rate among field agents
- Auto-account creation matches existing chart (no company, name = account_name with -ABBR suffix)
- Agent hierarchy walked from customer's default_sales_agent up through parent_agent chain

### Test Results
```
Invoice: DP-SINV-07-25-0006
Grand Total: 15000.0
Outstanding: 13500.0
  Commission - Karachi Head:     amt=75.0   account=Commission Expense - GLPK
  Commission - Karachi Regional: amt=150.0  account=Commission Expense - GLPK
  Commission - Karachi Distributor: amt=300.0  account=Commission Expense - GLPK
  Commission - Asif Ali:         amt=225.0  account=Commission Expense - GLPK
  Retention 10%:                 amt=1500.0 account=Retention Receivable - GLPK
GL: Dr Commission Expense 750 / Cr Sales Commission Payable 750 — Balanced 17250/17250
```

### Issues Found & Resolved
1. `_find_parent` only queried by company; root accounts have company=NULL → fallback added for NULL company
2. `ensure_account` set company but parent had company=NULL → validation threw → fix: no company, ignore_mandatory
3. Account autoname = field:account_name → explicit name ignored → fix: use full_name as account_name
4. Split functions used agent's payable account as `account` field → Dr/Cr to same account → fix: pass expense_account

### Commits
- `de123ee` — Commission Phase 2: hierarchy, split, GL, _find_parent/ensure_account fixes
- `c6e0a54` — Unified CT Engine: effect+direction 2-axis model + distribution + auto-accounts
- `6a2b01d` — Phase 1c: Commercial Terms GL integration in make_gl_entries()

### Next Steps
- Commission Ledger doctype
- Commission Payment workflow
- Agent Dashboard / Reports
- Credit Note / Returns handling
- Multiple Commission rules per template
- Rule Based split method wiring
- Recoverable commission workflow
- party_ledger_impact wiring

## 2026-07-05 — Docs Audit + Repo Map Refresh

### Summary
- Added a root `README.md` for ERPMax with the current product introduction, feature map, page/workspace mapping, E2E status, gaps, and buy-me-a-coffee snippet.
- Added `docs/audit/COMPARATIVE_AUDIT.md` with a comparison against ERPNext, Odoo, Tryton, Dolibarr, and enterprise ERP expectations.
- Added `docs/REPO_TREE.md` with a functional repository tree view and linked both files from `docs/README.md`.

### Current State
- The repo docs now reflect the current source scan instead of the older placeholder snapshot.
- `Taxation` is still listed in `modules.txt`, but there is no dedicated `erpmax/taxation/` source tree yet.

### Next Steps
1. Run live-site E2E verification for the desk flows listed in the new README.
2. Clean up the hooks/report path inconsistencies called out in the audit.
3. Decide whether `Taxation` should own the ZATCA tree or remain folded into `e_invoicing`.

## 2026-07-05 — Missing Terms DocType + Hook Cleanup

### Summary
- Added the missing `Terms and Conditions` DocType so `Company.default_selling_terms` and `Company.default_buying_terms` can resolve.
- Cleaned `hooks.py` path mappings for the existing Company, Account, and Item Category tree scripts.
- Added `inventory/doctype/item_category/item_category_tree.js` and tree controller helpers in `item_category.py`.

### Verification
- `python -m py_compile "E:\Projects\erpmax\erpmax\hooks.py" "E:\Projects\erpmax\erpmax\inventory\doctype\item_category\item_category.py" "E:\Projects\erpmax\erpmax\erpmax\doctype\terms_and_conditions\terms_and_conditions.py"`

### Next Steps
1. Reload Desk and confirm Company form opens without the missing DocType error.
2. Verify the Item Category tree loads from the new hook path.

## 2026-07-05 — Activity Log Import Fix

### Summary
- Added `erpmax/erpmax/doctype/activity_log/__init__.py` so the `Activity Log` package imports cleanly during `bench migrate`.

### Verification
- Confirmed the doctype folder was present but missing the package marker.

### Next Steps
1. Re-run `bench migrate` on the site.
2. If a new import error appears, fix the next missing package or path in the same way.

## 2026-07-05 — Local Hooks + Report Path Cleanup

### Summary
- Read the local `E:\Projects\erpmax` working copy first, then reconciled `erpmax/hooks.py` against the actual local file tree.
- Removed dead hook targets for missing login/test utilities, dead scheduler imports, and dead Company `doc_events` function paths.
- Added missing API wrappers for `import_chart_of_accounts` and `get_naming_series_options` so the advertised whitelisted methods now resolve.
- Updated `report_builder.py` local fallback handling so reports that return `(columns, data)` no longer crash.

### Test Results
- `python -m py_compile "E:\Projects\erpmax\erpmax\hooks.py" "E:\Projects\erpmax\erpmax\accounting\api\coa.py" "E:\Projects\erpmax\erpmax\utils\naming.py" "E:\Projects\erpmax\erpmax\erpmax\page\report_builder\report_builder.py"`
- Result: no output, compile passed.

### Issues Found & Resolved
- `scheduler_events` referenced missing `auto_create_fiscal_year` and `renew_csid_if_needed` symbols locally -> removed dead scheduler entries.
- `doc_events` for Company pointed at module-level functions that do not exist in `company.py` -> removed dead hook entries and kept the Document class methods.
- `on_login` and `before_tests` pointed at non-existent `erpmax.utils.user` / `erpmax.utils.test_utils` modules -> removed dead hooks.
- `whitelisted_methods` exposed `import_chart_of_accounts` and `get_naming_series_options`, but neither function existed -> added wrappers.
- Local `report_builder.py` assumed every report `execute()` returned 4 values -> now handles both 2-value and 4-value report signatures.

### Next Steps
1. Decide whether to remove or replace the dead `standard_portlets` `/app/financial-summary` route.
2. Sync the remaining local page fixes (`control_room.py`, `settings_page.py`) with the already-documented VPS fixes if this local copy is still meant to be maintained.

## 2026-07-05 — Hook Path Cleanup

### Summary
- Fixed the `erpmax-dashboard` page hook to point at the real file path: `accounting/page/erpmax_dashboard/erpmax_dashboard.js`.
- Removed the stale `setup_wizard` hook entries from `hooks.py` because the referenced file and methods do not exist in the current tree.

### Verification
- Verified `setup_wizard` no longer appears in `hooks.py`.
- Verified the dashboard page JS target exists on disk.

### Next Steps
1. Keep scanning for any other stale hook or report references when new pages or reports are added.

## 2026-07-05 — Stale Hook Sweep

### Summary
- Removed the stale `boot_session` hook from `hooks.py` because no `erpmax/boot.py` exists in the current tree.
- Removed the stale `email_hooks` entry for `Sales Invoice` because `send_invoice_email` does not exist in the current `sales_invoice.py`.
- Fixed the wrong import path in `erpmax/erpmax/doctype/company/company.py` so company account setup now imports from `erpmax.erpmax.doctype.company_account_setup.company_account_setup`.

### Verification
- Verified `boot_session` and `send_invoice_email` no longer appear in `hooks.py`.
- Verified the `company_account_setup` import now matches the actual file location.

### Next Steps
1. Continue path sweeps whenever hooks, pages, or reports are added.

## 2026-07-05 — Company Permission + Workspace Repair Helper

### Summary
- Added `get_permission_query_conditions` and `has_permission` to `erpmax/erpmax/doctype/company/company.py` so the Company list view hook resolves.
- Added `fixing/repair_workspace_content.py` to rebuild workspace `content` JSON from `Workspace Link` rows when the stored JSON is malformed.

### Verification
- `py_compile` passed for the touched Python files.

### Next Steps
1. Run the workspace repair helper on the live site to fix the broken Workspace JSON payload.

## 2026-07-05 — Workspace Helper Cleanup

### Summary
- Added `--dry-run` and optional single-workspace repair support to `fixing/repair_workspace_content.py`.
- Guarded the legacy workspace update scripts against missing workspace directories and switched file reads to UTF-8.

### Verification
- `py_compile` passed for `repair_workspace_content.py`, `update_ws_db.py`, and `final_workspace_fix.py`.

### Next Steps
1. Use `--dry-run` first when repairing live workspace content.

## 2026-07-05 — Go Services Verification

### Summary
- Added the missing Go module dependencies for Redis and WebSocket support in `go-services/go.mod`.
- Ran `go test ./...` in `E:\Projects\erpmax\go-services` and the service layer now compiles cleanly.

### Result
- The Go services are usable as a standalone helper layer for ERPMax.
- The Python client wrapper exists in `erpmax/utils/go_services_client.py`.
- The core ERPMax app does not automatically route desk traffic through Go services yet; integration is optional and explicit.

### Next Steps
1. Wire specific ERPMax screens or endpoints to the Go client only where there is a real speed benefit.

## 2026-07-05 — Go Services Runtime Fixes

### Summary
- Added the missing Go dependencies for Redis and WebSocket support.
- Fixed invalid Frappe table names in Go SQL queries (`tabSales Invoice`, `tabPurchase Invoice`, `tabGL Entry`, `tabSales Invoice Tax`).
- Fixed the Go list-view query path so filter args and pagination args are actually passed into the SQL call.

### Verification
- `go test ./...` passes in `E:\Projects\erpmax\go-services`.

### Result
- Go services are now usable as a standalone helper layer for ERPMax.
- ERPMax still uses them only through the Python client wrapper unless you wire specific screens or calls to it.

## 2026-07-05 — VPS Asset and Hook Cleanup

### Summary
- Removed the dead `pdf_generator.js` hook reference and deleted `hooks_new.py` so `hooks.py` is the single hook source.
- Deployed `charts.js`, `report_engine.js`, and `charts.css` to the VPS.
- Rebuilt ERPMax assets on the VPS, restarted bench, and verified the asset URLs return `200 OK`.

### Current State
- The live 404s for `pdf_generator.js`, `charts.js`, `report_engine.js`, and `charts.css` are resolved.
- The deployed `hooks.py` now points at existing assets.

### Next Steps
1. Keep verifying the remaining hook/report registrations against the filesystem.
2. Run live-site E2E on the main desk flows after the asset cleanup.

## 2026-07-05 — Control Room Wiring

### Summary
- Wired the Control Room page to use Go services first for dashboard and chart data.
- Kept local Frappe queries as fallback for recent activities and system status.

### Verification
- `python -m py_compile E:\Projects\erpmax\erpmax\erpmax\page\control_room\control_room.py`

### Result
- Control Room now has a working Go-services acceleration path.

### Next Steps
1. If this performs well on the live site, wire List View or Report Builder next.

## 2026-07-05 — Comprehensive Plan Doc

### Summary
- Added `docs/planning/COMPREHENSIVE_PLAN.md` with the current ERPMax vision, milestone ladder, task list, and report definitions.
- Linked the new plan from `docs/planning/ROADMAP.md`.

### Result
- The repo now has a single planning doc that explains the product direction and the meaning of Sales Register and Purchase Register.

## 2026-07-05 — List View and Report Builder Wiring

### Summary
- Added `erpmax.utils.client` as the Frappe-facing bridge for Go-powered list view and report view calls.
- Wired `frappe.desk.reportview.get`, `frappe.desk.reportview.get_count`, `frappe.client.get_count`, and `frappe.desk.query_report.run` through the ERPMax client bridge with fallback.
- Updated the ERPMax `Report Builder` page to try Go services first before falling back to local report executors.

### Verification
- `python -m py_compile E:\Projects\erpmax\erpmax\utils\client.py E:\Projects\erpmax\erpmax\erpmax\page\report_builder\report_builder.py E:\Projects\erpmax\erpmax\hooks.py`

### Result
- List view browsing now has a Go acceleration path.
- Report builder now has a Go-first path for standard ERPMax reports.

### Next Steps
1. Validate list browsing and report rendering on the live site.
2. If stable, wire other heavy table/report screens next.

## 2026-07-05 — Expanded Report Surface

### Summary
- Expanded the report registry to cover the current ERPMax report set, including accounting, sales, banking, and project reports.
- Updated the Report Builder page to show more report cards and use a Go-first path with local fallback for every current report type.

### Verification
- `python -m py_compile E:\Projects\erpmax\erpmax\utils\client.py E:\Projects\erpmax\erpmax\erpmax\page\report_builder\report_builder.py`

### Result
- Report Builder now covers the current report surface more completely and can load from Go where supported.

### Next Steps
1. If you want directory normalization next, decide whether to introduce a new `report/` to `reports/` alias layer or keep the current Frappe naming.
