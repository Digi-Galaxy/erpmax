# ERPMax Vision

## Purpose

ERPMax is a modular ERP platform built on Frappe for service-heavy, project-driven, region-aware businesses that need strong accounting, billing, expense control, printing flexibility, and operational traceability.

It is intended to support real business scenarios such as:
- transport and dispatch operations
- recurring service invoicing
- project and contract billing
- petty cash and employee expense control
- retention-based customer billing
- country-specific and customer-specific print requirements
- regional e-invoicing and compliance workflows such as ZATCA

## Product Direction

ERPMax should become a practical business operating system that combines:
- ERPNext-style document reliability and accounting discipline
- modular business separation similar to mature ERP suites
- flexible document printing and communication behavior
- strong project, expense, and service profitability tracking
- support for regional tax and invoice compliance

## Core Product Principles

### 1. Modular by Business Domain
ERPMax should stay split into clear modules, not one overloaded root bucket.

Target modules include:
- Accounting
- Business Setup
- Commerce
- Sales
- Purchase
- Expense Management
- Inventory
- Project Management
- Reporting
- Printings
- E-Invoicing
- future Transport and Operations modules

### 2. Document-Driven Workflows
Business logic should be driven through auditable documents, not hidden state.

Examples:
- expense claims with approval and payment history
- invoices with recurring generation history
- send history through timeline comments instead of custom sent flags
- project costs linked to service, customer, and project

### 3. Strong Accounting Visibility
Every operational area should support financial meaning.

ERPMax should make it easy to answer:
- what did we bill?
- what did we spend?
- what is still outstanding?
- what cost belongs to which project, service, or customer?
- what is budgeted vs actual?

### 4. Customer-Specific Commercial Behavior
Different customers often require different billing behavior.

ERPMax should support:
- retention defaults
- customer-specific print format
- custom wording
- customer-specific terms and conditions
- table layout differences
- customer-specific language and letterhead choices

### 5. Regional and Multi-Country Readiness
ERPMax should remain ready for country-specific behavior without hardcoding one country into the whole product.

It should support:
- localized date, currency, and country defaults
- tax and invoice compliance modules
- Arabic/Urdu and multilingual print behavior
- customer and company printing rules by country or business type

### 6. Traceability Over Hidden Flags
Where possible, ERPMax should prefer timeline, comments, communications, and document relations over one-off custom flags.

This supports:
- auditability
- fewer sync bugs
- easier investigation of business mistakes
- safer resend and approval behavior

## Intended User Groups

ERPMax is intended for:
- owners and finance managers
- accountants and accounts users
- sales and billing teams
- project and service managers
- operations teams in transport and field service businesses
- businesses working with contract billing, project costs, and repeat invoicing

## Long-Term Product Goals

### Near-Term
- finish the module split cleanly
- stabilize recurring invoices
- stabilize send/print behavior
- build project profitability visibility
- build reporting definitions and charts
- build advanced invoice print rendering

### Mid-Term
- complete transport workflows
- complete project lifecycle workflows
- build stronger reporting and dashboard system
- add print-profile and communication templates by customer / document type
- add recurring automation scheduler

### Long-Term
- mature ERPMax into a complete modular ERP product with:
  - accounting depth
  - project profitability
  - recurring commercial flows
  - region-aware printing and compliance
  - optional SaaS readiness through separate Frappe sites per business

## Strategic References

ERPMax should continue learning from:
- ERPNext and Frappe for document and framework discipline
- Odoo, Tryton, OFBiz, iDempiere, Dolibarr, Akaunting, and others under `E:\library\_ref\erp`
- Daftra for modular business UX references
- Manager project discipline for product planning, roadmap, gaps, and session tracking

## Success Criteria

ERPMax is succeeding when a business can:
- run daily invoices, expenses, and projects without manual spreadsheets
- control who approved, paid, sent, and billed each document
- track project and service profitability in one place
- avoid duplicate sends and communication mistakes
- handle customer-specific billing/printing rules without hacks
- extend to new domains through modules rather than breaking old ones
