# ERPMax Comparative Audit

## Scope
Source scan of the current ERPMax repo, compared against mature ERP patterns from ERPNext/Frappe, Odoo, Tryton, Dolibarr, and common SMB accounting stacks.

## Baseline
- Standalone Frappe v15 app.
- 13 modules in `modules.txt`.
- 104 doctypes, 23 reports, 4 pages, 9 workspaces in the current status docs.
- ZATCA/FBR, sales, purchase, banking, inventory, project, expense, and reporting code all exist.

## What ERPMax Already Covers Well
| Area | ERPMax status | Why it matters |
|---|---|---|
| Company setup | Strong | Rich company profile, feature tiers, region/distributor hooks, tax/compliance fields |
| Core accounting | Strong | Accounts, GL, journal, payment, fiscal year, trial balance, P&L, balance sheet |
| Sales docs | Good | Quotation, proforma, SO, DN, SI, credit note, recurring billing, transport delivery |
| Purchase docs | Good | Supplier, PO, PI, debit note, supplier quotation |
| Banking | Good | Bank account, statement, transaction, reconciliation rules, bank reconciliation |
| Inventory | Good | Item, category, pricing, warehouse, stock ledger, stock entry |
| Compliance | Good | ZATCA/FBR scaffolding and company-level toggle fields |
| Reporting surfaces | Good | Dashboard, control room, report builder, standard reports |
| Performance layer | Good | Go services for search, list view, print, dashboard, cache, jobs |

## Comparison With Other ERPs
| ERP | Strengths ERPMax already matches | Gaps versus that ERP |
|---|---|---|
| ERPNext | Document-centric accounting and business flows | Full master coverage, workflows, multi-currency, broader test coverage, mature ecosystem parity |
| Odoo | Modular business apps and flexible workflows | Polished app breadth, automation depth, portal/eCommerce maturity, manufacturing/HR breadth |
| Tryton | Clean accounting and modular design | Smaller gap in architecture, but ERPMax still needs deeper transactional completeness |
| Dolibarr | Lightweight SMB orientation | ERPMax has richer compliance/accounting intent, but still lacks many mature SMB conveniences |
| SAP B1 / NetSuite class | Finance rigor and controls | Advanced approvals, audit controls, enterprise workflows, global compliance depth |

## Missing Areas
### Accounting / Finance
- Multi-currency.
- Credit note / debit note completion across every posting path.
- Stronger reconciliation automation and exception handling.
- Budgeting, cash flow, advanced cost center logic, fixed assets, depreciation lifecycle.
- More complete partner/shareholder capital tracking.

### Sales / Commerce
- CRM pipeline depth.
- Quotations and order automation depth.
- Returns, credit memo, pricing rule maturity.
- Portal/self-service surfaces.

### Purchase / Supply Chain
- Procurement approval workflows.
- Vendor performance and sourcing controls.
- Inventory valuation depth and stock audit tooling.

### Inventory / Warehouse
- Batch/serial/lot controls.
- Multi-warehouse process depth.
- Better stock adjustment and landed cost workflows.

### Projects / Services
- Stronger project billing, task, and profitability automation.
- Time tracking and service delivery controls.

### Compliance / Localization
- Final ZATCA validation matrix.
- FBR sandbox/prod test matrix.
- Multi-country tax packs beyond current focus.

### Platform / Operations
- Full regression and browser E2E coverage.
- Hook cleanup and path normalization.
- Better release checklist and upgrade notes.
- Transport module is absent from this repo.

## Concrete Repo Gaps Found From Scan
- `Taxation` is listed in `modules.txt`, but there is no dedicated `erpmax/taxation/` source tree.
- `e_invoicing` still carries the ZATCA work, so module naming needs final cleanup if Taxation is intended to own it.
- Some hooks and report paths still need cleanup between `hooks.py` and the current runtime tree.
- The project state docs already flag missing multi-currency and incomplete purchase GL posting.

## Reference Libraries / Upstream References
- Frappe v15 app model.
- ERPNext accounting and document flow patterns.
- Odoo modular ERP patterns.
- Tryton module separation patterns.
- Dolibarr SMB ergonomics.
- WeasyPrint, Jinja2, Pillow, pandas, openpyxl, numpy, qrcode, cryptography, requests, Flask, Flask-CORS.
- Go services for fast read-heavy endpoints.

## Priority Gaps
1. Finish core financial correctness first.
2. Clean module ownership and hooks.
3. Add E2E and regression coverage.
4. Close compliance validation gaps.
5. Expand business modules only after core accounting is stable.

## Audit Conclusion
ERPMax is not a thin ERPNext wrapper. It already has a real standalone ERP shape, especially in accounting, sales, banking, compliance, and reporting. The main gap is breadth and hardening: missing enterprise workflows, incomplete financial edge cases, and missing regression proof.
