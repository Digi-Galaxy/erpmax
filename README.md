# ERPMax

ERPMax is a standalone Frappe v15 ERP app for accounting, sales, purchase, inventory, banking, projects, compliance, and reporting.

## What Exists
- Standalone app, `frappe` only.
- 13 business modules in `modules.txt`.
- 104 doctypes, 23 reports, 4 pages, 9 workspaces in the current scan.
- Core areas: Company setup, Accounting, Banking, Business Setup, Commerce, Inventory, Sales, Purchase, Project Management, Expense Management, Reporting, Printings, stock, and e-invoicing.
- `Taxation` is listed in `modules.txt`, but the dedicated source tree is not yet separate in this scan.
- E-invoicing support is present through ZATCA/FBR-related doctypes and utilities.
- Go services exist for caching, list view, print, dashboard, search, import/export, websocket, and bulk operations.

## Main Features
- Company setup with tabs, feature tiering, multi-branch toggles, region and distributor links.
- Accounting core: account tree, fiscal year, journal entry, payment entry, GL, trial balance, balance sheet, P&L, tax, statements.
- Sales flow: quotation, proforma invoice, sales order, delivery note, sales invoice, credit note, recurring invoice, transport delivery.
- Purchase flow: supplier, quotation, purchase order, purchase invoice, debit note.
- Banking flow: bank account, bank statement, bank transaction, reconciliation rules, bank reconciliation.
- Inventory flow: item, item category, price list, item price, pricing rule, warehouse, stock entry, stock ledger entry.
- Business setup: region, distributor, distributor commission.
- Project and expense support: project, project service, expense claim, expense type.
- Reporting and surfaces: Control Room, ERPMax Dashboard, Settings Page, Report Builder.

## Real Surfaces
- `Control Room` - live metrics and recent activity.
- `ERPMax Dashboard` - accounting equation, balance sheet / P&L boxes, recent voucher feed.
- `Settings Page` - system info, module status, cache and asset tools.
- `Report Builder` - custom report builder for doctypes and saved reports.

## Workspace Map
- `Accounts` - accounting, banking, reconciliation, reports.
- `Sales` - quotations, sales order, invoice, delivery, commission.
- `Purchase` - supplier, quotation, PO, invoice, debit note.
- `Inventory` - items, categories, pricing, warehouse, stock.
- `Projects` - project billing and profitability.
- `Compliance` - ZATCA and FBR work.
- `Setup` - company and configuration.

## E2E Status
- This workspace scan did not execute browser E2E tests.
- The current codebase already contains the post-fix desk pages and dashboard wiring.
- Before release, run the live-site E2E flow for Company, Sales Invoice, Payment Entry, Purchase Invoice, Bank Reconciliation, and Control Room.

## Gaps
- No full ERPNext parity.
- No transport module inside this repo.
- Multi-currency is still missing.
- Credit note / debit note and other accounting edge workflows are incomplete.
- Regression coverage is incomplete.
- Some hooks and report paths still need cleanup.
- `Taxation` is listed in `modules.txt`, but there is no dedicated `erpmax/taxation/` source tree yet.

## Buy Me a Coffee
Add a link like this in the app footer, a page, or a custom desk card:

```html
<a href="https://www.buymeacoffee.com/yourname" target="_blank" rel="noopener noreferrer">Buy me a coffee</a>
```

## Comparison Audit
See `docs/audit/COMPARATIVE_AUDIT.md`.

## Repository Tree
See `docs/REPO_TREE.md`.

## Notes
- ERPMax is standalone and should be evaluated as its own ERP, not as an ERPNext add-on.
- Current docs and source scans are the truth source for this snapshot.
