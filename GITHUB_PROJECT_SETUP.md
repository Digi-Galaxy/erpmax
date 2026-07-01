# ERPMax GitHub Project Setup

## Target
Repository project for:
- `https://github.com/Digi-Galaxy/erpmax/projects`

Current observed state:
- no repository project exists yet

## Recommended Project Name
`ERPMax Product Roadmap`

## Purpose
Use GitHub Projects for execution tracking, not as the only source of product design.

GitHub Project should track:
- roadmap items
- active work
- bugs
- blocked items
- module-specific delivery

Product design and architecture should remain in repo docs such as:
- `VISION.md`
- `ROADMAP.md`
- `GAPS.md`
- `DISCOVERY.md`
- `SESSION_STATUS.md`

## Recommended Views

### 1. Backlog
Shows all planned items not yet started.

### 2. Current
Shows current working sprint or immediate implementation batch.

### 3. Bugs
Shows defects, regressions, and structural cleanup items.

### 4. Modules
Groups issues by ERPMax module.

### 5. Printing
Focus view for print and communication features.

### 6. Reporting
Focus view for reports, charts, dashboards, and analytics.

### 7. Transport
Focus view for delivery, dispatch, route, trip, and vehicle workflows.

## Recommended Custom Fields

### Status
Options:
- Backlog
- Ready
- In Progress
- Blocked
- Review
- Done

### Priority
Options:
- P0 Critical
- P1 High
- P2 Medium
- P3 Low

### Module
Options:
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
- ERPMax Legacy
- Cross Module

### Area
Options:
- Product
- Workflow
- Data Model
- Reporting
- Printing
- Integration
- Compliance
- UX
- Cleanup

### Phase
Options:
- Phase 1 Foundation
- Phase 2 Billing
- Phase 3 Printings
- Phase 4 Expense
- Phase 5 Projects
- Phase 6 Reporting
- Phase 7 Transport
- Phase 8 Compliance
- Ongoing Cleanup

### Reference
Short text field for noting inspiration/source such as:
- ERPNext
- Odoo
- Manager
- Daftra
- library_ref/erp

## First Cards To Create

### Foundation / Cleanup
- Move `Credit Details` to final module home
- Move `Documents` to final module home
- Audit compatibility wrappers and cleanup plan

### Sales
- Automatic recurring invoice scheduler
- Recurring invoice due list / dashboard
- Send history dialog on Sales Invoice
- Transport delivery fields on Sales Invoice
- WhatsApp/email resend policy improvements

### Printings
- Implement invoice table format rendering in Jinja print templates
- Implement customer wording and terms in final print output
- Implement customer print format override resolution in final print flow
- Add print policy matrix by doctype and customer

### Expense Management
- Add approval action workflow for expense claims
- Add payment release action flow for expense claims
- Add petty cash settlement flow
- Add budget vs actual report for expenses

### Project Management
- Build project profitability report
- Build project lifecycle stages
- Add maintenance / construction / subcontract project flows

### Reporting
- Create `Report Definition` doctype
- Create `Chart Definition` doctype
- Create `Report Filter Template` doctype
- Build first project profitability dashboard

### Transport
- Add driver, vehicle, route, trip fields
- Add POD / delivery proof handling
- Add third-party transporter support
- Link dispatch cost to invoice and project profitability

## Workflow Rule
1. Repo docs define the why and the architecture
2. GitHub issues define individual work items
3. GitHub Project tracks status across those issues
4. Session files record actual execution history

## Suggested Setup Order
1. Create the project `ERPMax Product Roadmap`
2. Add custom fields
3. Create the recommended views
4. Seed cards from `ROADMAP.md` and `GAPS.md`
5. Convert high-priority cards into issues
6. Use `Current` as the active execution board
