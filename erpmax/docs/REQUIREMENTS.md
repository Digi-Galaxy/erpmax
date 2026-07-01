# ERPMax — Feature Requirements & Tracking

> Single source of truth. Every feature requested, its status, and what remains.

---

## PHASE 1 — Foundation (Done)

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1.1 | Frappe v15 Standalone App | ✅ Done | No ERPNext dependency. Owns all doctypes. |
| 1.2 | VPS Provisioning | ✅ Done | Ubuntu 26.04, Python 3.11.11, MariaDB 11.8.6, bench v15.113.3 |
| 1.3 | Git Setup | ✅ Done | `github.com/Digi-Galaxy/erpmax.git` (develop branch) |
| 1.4 | Multi-Country E-Invoicing | ✅ Done | ZATCA, FBR, ETA, FTA providers. Abstract BaseProvider architecture. |
| 1.5 | ERPMax Settings | ✅ Done | Feature toggles (show_previous_balance, cnic_mandatory, advanced_address, urdu_font, transport_module, project_invoicing) |
| 1.6 | Company Setup | ✅ Done | 56 fields. FBR tab, ZATCA tab, COA template selection. |
| 1.7 | Chart of Accounts | ✅ Done | 5 standards (Pakistan-ICAP, IFRS, Saudi-SOCPA, UAE, US GAAP). Tree builder with one-click create. |
| 1.8 | Customer / Item / Project | ✅ Done | Customer (34 fields), Item (19 fields), Project (20 fields with Cost Centre auto-create). |
| 1.9 | Address Management | ✅ Done | Multi-country format. Building number, street, district, city, postal. |
| 1.10 | Sales Invoice | ✅ Done | 101 fields. Embedded payment, retention, outstanding, e-invoicing, project/cost centre links. |

---

## PHASE 2 — Assets & UI (Next)

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 2.1 | Currency Symbol Fonts | 🔲 Pending | Add fonts to `erpmax/public/fonts/` for PKR, SAR, AED, USD symbols |
| 2.2 | Urdu/Arabic Font Support | 🔲 Pending | Add Urdu/Arabic fonts (Noto Nastaliq Urdu, Noto Kufi Arabic) |
| 2.3 | Simple Sales Invoice UI | 🔲 Pending | Clean, minimal print format + desk form customization |
| 2.4 | Custom Desk CSS/Branding | 🔲 Pending | ERPMax custom theme, logo, favicon |

---

## PHASE 3 — Expense Management

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 3.1 | Employee Doctype | 🔲 Pending | Employee master (name, department, designation, mobile, email, joining date) |
| 3.2 | Expense Type Doctype | 🔲 Pending | Categories: Travel, Meals, Fuel, Office Supplies, Utilities, etc. |
| 3.3 | Expense Claim Doctype | 🔲 Pending | Employee expense claim with child table, approval workflow |
| 3.4 | Expense Entry / Payment | 🔲 Pending | Post approved expense to accounting (debit expense, credit payable) |

---

## PHASE 4 — Purchase Management

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 4.1 | Supplier Doctype | 🔲 Pending | Supplier master (NTN, STRN, CRN, address, contacts) |
| 4.2 | Purchase Order Doctype | 🔲 Pending | PO with items, rates, taxes, delivery dates, approval workflow |
| 4.3 | Purchase Receipt Doctype | 🔲 Pending | Goods receipt against PO (stock / non-stock items) |
| 4.4 | Purchase Invoice Doctype | 🔲 Pending | Supplier bill with PO matching, tax calculation, payment tracking |
| 4.5 | Supplier Quotation Doctype | 🔲 Pending | RFQ from suppliers |

---

## PHASE 5 — Payment & Accounting

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 5.1 | Payment Entry Doctype | 🔲 Pending | Standalone payment (customer receipt / supplier payment). Bank/cash mode. |
| 5.2 | Payment Reconciliation | 🔲 Pending | Match payments against invoices, settle outstanding |
| 5.3 | Journal Entry Doctype | 🔲 Pending | Double-entry accounting (debit/credit with GL posting) |
| 5.4 | Bank Account Doctype | 🔲 Pending | Bank master linked to Account |

---

## PHASE 6 — Financial Reports

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 6.1 | Profit & Loss Statement | 🔲 Pending | Standard P&L with period comparison (monthly/quarterly/yearly) |
| 6.2 | Balance Sheet | 🔲 Pending | Assets = Liabilities + Equity |
| 6.3 | Trial Balance | 🔲 Pending | Debit/credit listing of all accounts |
| 6.4 | General Ledger | 🔲 Pending | Account-wise transaction history |
| 6.5 | 2-Column Income & Expenditure | 🔲 Pending | Side-by-side income vs expense comparison |
| 6.6 | Accounts Receivable Report | 🔲 Pending | Customer-wise outstanding |
| 6.7 | Accounts Payable Report | 🔲 Pending | Supplier-wise outstanding |

---

## PHASE 7 — Transport System

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 7.1 | Install transport_app on site | 🔲 Pending | Activate existing transport_app on erpmax.celtcoksa.com |
| 7.2 | Transport doctypes | 🔲 Pending | Vehicle, Driver, Trip, Booking, Route, Delivery |
| 7.3 | Delivery Charges in SI | 🔲 Pending | Link transport trip to sales invoice for delivery charges |
| 7.4 | Free Delivery Policy | 🔲 Pending | Configure free delivery thresholds in ERPMax Settings |

---

## PHASE 8 — Sales Workflow

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 8.1 | Quotation Doctype | 🔲 Pending | Customer quote → accepted → Sales Order |
| 8.2 | Sales Order Doctype | 🔲 Pending | Confirmed order → reserved items → SI |
| 8.3 | Quotation → SO → SI workflow | 🔲 Pending | Copy-to buttons: Quot → SO → SI with draft status |
| 8.4 | Draft affects reports | 🔲 Pending | Draft Sales Orders/Invoices visible in sales reports/charts |

---

## PHASE 9 — Portal & Website

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 9.1 | Customer Portal | 🔲 Pending | Customer login, view invoices, payments, outstanding |
| 9.2 | Web Forms | 🔲 Pending | Contact us, quote request, expense submission |
| 9.3 | Company Website Pages | 🔲 Pending | About, services, contact (Frappe web pages) |

---

## PHASE 10 — Additional Accounting

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 10.1 | Fiscal Year Management | ✅ Done | Year start/end dates |
| 10.2 | VAT Process | ✅ Done | VAT return calculation and processing |
| 10.3 | Cost Centre Accounting | ✅ Done | Cost centre allocation on transactions |
| 10.4 | Budget Management | 🔲 Pending | Budget against cost centre / project |

---

## PHASE 11 — Library Dependencies

| # | Dependency | Status | Details |
|---|-----------|--------|---------|
| 11.1 | qrcode / PyQRCode | 🔲 Check | For QR generation on invoices |
| 11.2 | babel | 🔲 Check | For number/currency formatting |
| 11.3 | hijri-converter | 🔲 Check | For Hijri date support |
| 11.4 | twilio / SMS | 🔲 Check | For SMS notifications |
| 11.5 | highcharts / charts | 🔲 Check | For dashboard charts |

---

## Current Priority Order

1. ✅ Phase 1 — Foundation (DONE)
2. 🔲 Phase 2 — Assets & UI (Currency fonts, Urdu fonts, Simple SI UI)
3. 🔲 Phase 3 — Expense Management
4. 🔲 Phase 4 — Purchase Management
5. 🔲 Phase 5 — Payment & Accounting
6. 🔲 Phase 6 — Financial Reports
7. 🔲 Phase 7 — Transport System
8. 🔲 Phase 8 — Sales Workflow
9. 🔲 Phase 9 — Portal & Website
10. 🔲 Phase 10 — Additional Accounting
11. 🔲 Phase 11 — Library Dependencies

---

*Last updated: 2026-07-01*
*Maintainer: Galaxy Labs*
