# ERPMax — Codebase Scan

## Project Structure
```
E:\Projects\erpmax\
├── AGENTS.md                      # Agent routing
├── PROJECT_DESCRIPTION.md         # Project overview
├── WORKING_UNDERSTANDINGS.md      # Design decisions
├── ROADMAP.md                     # Milestones
├── TASKS.md                       # Active tasks
├── SESSION_STATUS.md              # Current state
├── VISION.md                      # Long-term vision
├── VPS_ACCESS.md                  # Server details
├── MILESTONES.md                  # Milestones
├── erpmax/                        # Frappe app source
│   ├── accounting/                # Accounting module
│   ├── banking/                   # Banking module
│   ├── business_setup/            # Business setup
│   ├── commerce/                  # Commerce (Sales Agent, etc.)
│   ├── commercial_terms/          # CT Engine (evaluator, hooks)
│   ├── e_invoicing/               # E-invoicing (FBR, ZATCA)
│   ├── erpmax/                    # Core (settings, pages)
│   ├── expense_management/        # Expenses
│   ├── inventory/                 # Inventory
│   ├── printings/                 # Print formats
│   ├── project_management/        # Projects
│   ├── public/                    # Static assets
│   ├── purchase/                  # Purchase module
│   ├── reporting/                 # Reports
│   ├── sales/                     # Sales (SI, Quo, SO, DN)
│   ├── setup/                     # Setup
│   ├── stock/                     # Stock
│   └── utils/                     # Utilities
├── ai/                            # Agent intelligence
│   ├── agents/                    # Agent behavior files
│   │   ├── agent-knowledge-workflow.md
│   │   ├── NOTES.md
│   │   ├── MISTAKES.md
│   │   └── USER_INSTRUCTIONS.md
│   ├── memory/                    # Session memory
│   │   ├── session-chat.md
│   │   └── codebase-scan.md
│   ├── projects/                  # Feature-area tracking
│   └── knowledge/                 # Cross-session discoveries
│       └── discoveries.md
└── go-services/                   # Go backend services
```

## Key Modules
- **commercial_terms**: CT Engine with evaluator.py (GL_MAP, ensure_account, _find_parent, hierarchy split)
- **commerce**: Sales Agent doctype, Customer modifications
- **accounting**: Account doctype with validate_parent_company(), GL Entry
- **e_invoicing**: FBR/ZATCA provider architecture
- **sales**: Sales Invoice with make_gl_entries()

## Active Capabilities
- Commercial Terms Engine: 7 GL patterns (effect×direction), auto-account creation, distribution
- Commission: Agent hierarchy, split methods (Hierarchy, Percentage), GL integration
- Feature Toggles: ERPMax Settings controls (enable_sales_retention, etc.)
- E-Invoicing: FBR Pakistan + ZATCA Saudi Arabia (abstract provider)
- Sales Chain: Quotation → SO → DN → SI

## VPS State (erpmax.celtcoksa.com)
- HEAD: de123ee (Commission Phase 2)
- Chart of Accounts: root accounts (Asset, Liability, Income, Expense) with company=NULL
- Custom accounts: Retention Receivable - GLPK, Commission Expense - GLPK, Sales Commission Payable - GLPK
- Doctypes: Sales Agent created, Customer with default_sales_agent, CT Template with commission fields
- 4 Sales Agents in hierarchy: Karachi Head → Regional → Distributor → Asif Ali

## Docs Refresh (2026-07-05)
- Added root `README.md` for the current ERPMax introduction, features, E2E status, gaps, and donation link.
- Added `docs/audit/COMPARATIVE_AUDIT.md` for ERP comparisons and feature gap analysis.
- Added `docs/REPO_TREE.md` for the functional repository tree.
- Updated `docs/README.md` to link the new audit and tree documents.
- New scan note: `Taxation` is listed in `modules.txt`, but there is no dedicated `erpmax/taxation/` source tree yet.

## Hook Cleanup (2026-07-05)
- `hooks.py` now points `Company` to the real `erpmax/doctype/company/company.js` file.
- `hooks.py` tree mappings now point to the real `accounting`, `erpmax`, and `inventory` tree scripts.
- Added `inventory/doctype/item_category/item_category_tree.js` plus tree helpers in `item_category.py`.
- Added the missing `Terms and Conditions` DocType for Company term links.

## Activity Log Import Fix (2026-07-05)
- Added `erpmax/erpmax/doctype/activity_log/__init__.py` to allow `erpmax.erpmax.doctype.activity_log.activity_log` imports during migrate.

## Hook Cleanup (2026-07-05)
- `hooks.py` now points `page_js` to the real dashboard file path: `accounting/page/erpmax_dashboard/erpmax_dashboard.js`.
- Removed stale `setup_wizard` hook entries because the referenced file and methods do not exist in the current tree.
- Removed stale `boot_session` and `email_hooks` entries from `hooks.py`.
- Fixed the `company_account_setup` import path in `erpmax/erpmax/doctype/company/company.py`.

## Workspace Repair Helper (2026-07-05)
- Added `fixing/repair_workspace_content.py` to rebuild `Workspace.content` JSON from `Workspace Link` rows and correct malformed workspace payloads on the live site.
- Added dry-run and single-workspace support to the repair helper.
- Hardened the older workspace update scripts against missing directories and UTF-8 read issues.

## Go Services Verification (2026-07-05)
- Added missing Go dependencies for `github.com/redis/go-redis/v9` and `github.com/gorilla/websocket`.
- `go test ./...` passes in `E:\Projects\erpmax\go-services`.
- The Python client wrapper exists, but ERPMax does not yet auto-wire desk traffic through the Go layer.
- Fixed invalid table-name SQL in Go services and wired list-view query args correctly.

## Control Room Wiring (2026-07-05)
- Control Room now tries Go services first for dashboard and chart data via `GoServicesClient.get_dashboard()`.
- Local Frappe data remains as fallback for recent activities and system status.

## List View and Report Builder Wiring (2026-07-05)
- Added `erpmax.utils.client` as the bridge for Go-backed list view and report view calls.
- Hooked `frappe.desk.reportview.get`, `frappe.desk.reportview.get_count`, `frappe.client.get_count`, and `frappe.desk.query_report.run` through the bridge.
- `Report Builder` now tries Go services first for standard ERPMax reports.
- Expanded the report surface shown in `report_builder.js` to include the current accounting, sales, banking, and project reports.

## Comprehensive Plan Doc (2026-07-05)
- Added `docs/planning/COMPREHENSIVE_PLAN.md` with vision, milestones, tasks, and report definitions.

## VPS Asset Cleanup (2026-07-05)
- Removed `hooks_new.py` and kept `hooks.py` as the single hook source.
- Removed the stale `pdf_generator.js` asset reference.
- Deployed `charts.js`, `report_engine.js`, and `charts.css` to the VPS and rebuilt assets.
- Verified `https://erpmax.celtcoksa.com/assets/erpmax/js/charts.js`, `report_engine.js`, and `css/charts.css` return `200 OK`.
