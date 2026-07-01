# ERPMax Modules

## Module Ownership Guide

This document defines the intended ownership and scope of each ERPMax module.

## ERPMax
**Purpose:** residual legacy bucket during migration only.

**Current doctypes:**
- `Credit Details`
- `Documents`

**Rule:**
No new business features should be added here. This module should eventually become empty or extremely minimal.

## Accounting
**Purpose:** financial core and posting-oriented accounting structures.

**Examples in this module:**
- `Account`
- `Chart of Accounts Template`
- `Cost Centre`
- `Fiscal Year`
- `Journal Entry`
- `Payment Entry`
- sales/purchase tax templates

**Owns:**
- account master structures
- journals
- accounting periods
- tax template structures
- accounting posting-facing doctypes

## Business Setup
**Purpose:** company, organization, and general business administration foundations.

**Examples in this module:**
- `Company`
- `Holiday List`
- `ERPMax Settings`
- `Employee`
- `Expense Claim`
- `Expense Claim Detail`

**Owns:**
- company settings
- employee master basics
- global ERPMax settings
- claim header flow for expenses

## Commerce
**Purpose:** customer-facing commercial master data and general trade-side support structures.

**Examples in this module:**
- `Customer`
- `Address`
- `Address Link`
- `VAT Process`
- `VAT Process Item`

**Owns:**
- customer master
- address relationships
- VAT process handling tied to commercial documents
- customer-specific commercial defaults

## Sales
**Purpose:** outbound billing and customer invoice flow.

**Examples in this module:**
- `Sales Invoice`
- `Sales Invoice Item`
- `Sales Invoice Tax`

**Owns:**
- sales billing documents
- recurring invoice behavior
- send / share actions for invoices
- transport delivery workflow in future

## Purchase
**Purpose:** inbound supplier purchasing documents.

**Examples in this module:**
- `Supplier`
- `Purchase Invoice`
- `Purchase Order`
- `Purchase Receipt`
- their child tables

**Owns:**
- supplier-side commercial documents
- buying flow
- purchase receipt and invoice chain

## Expense Management
**Purpose:** expense categorization, budget mapping, and company expense policy structures.

**Examples in this module:**
- `Expense Type`
- `Expense Type Account`

**Owns:**
- expense categories
- account mapping by company
- budget amount and budget period by expense type
- expense policy defaults

## Inventory
**Purpose:** item and stock/service commercial master.

**Examples in this module:**
- `Item`

**Owns:**
- item master
- service/product classification
- stock or service commercial setup
- future inventory/warehouse features if introduced

## Project Management
**Purpose:** projects, services, contract-oriented execution, and profitability foundation.

**Examples in this module:**
- `Project`
- `Project Service`

**Owns:**
- project master
- project contract structure
- service rows attached to project
- future maintenance / construction / vehicle / subcontract project flow

## Reporting
**Purpose:** reporting structures, generated report definitions, and chart/report setup.

**Examples in this module:**
- `Reporting Standard`
- `Reporting Standard Account`

**Owns:**
- reporting structures
- future chart definitions
- future report definitions
- future saved report filters and dashboards

## Printings
**Purpose:** print and PDF behavior across documents.

**Examples in this module:**
- `PDF Settings`

**Owns:**
- company print defaults
- customer override policy support
- future print mappings by doctype/customer
- future document output architecture

## E-Invoicing
**Purpose:** regional e-invoice compliance workflows.

**Examples in this module:**
- ZATCA-related doctypes and support records

**Owns:**
- compliance-specific invoice integration
- invoice clearance/reporting identifiers
- future country-specific e-invoicing extensions

## Future Modules Likely
- `Transport`
- `Operations`
- `Assets`
- `CRM`
- `HR`
- `Banking` if banking grows beyond accounting-level payment entry behavior

## Ownership Rules
1. New doctypes should be created in the correct business module, not in `ERPMax`
2. Customer-side invoicing behavior belongs in `Sales` or `Commerce`, not `Accounting`
3. Print and PDF execution rules belong in `Printings`
4. Report definition systems belong in `Reporting`
5. Expense policy and budget mapping belong in `Expense Management`
6. Project execution and service costing belong in `Project Management`
