# ERPMax Roadmap

## Status Summary

ERPMax has completed a major restructuring pass and now has a cleaner module layout, stronger expense workflows, recurring invoice foundations, customer-specific print defaults, and send-history logic.

The next roadmap should focus on completing operating workflows, reporting, printing execution, and transport/business-specific flows.

## Phase 1: Module Foundation and Stabilization

### Completed
- split core doctypes into business modules
- created live module structure for Accounting, Business Setup, Commerce, Purchase, Sales, Expense Management, Inventory, Project Management, Reporting, Printings, and E-Invoicing
- added compatibility wrappers for old imports
- reduced old `ERPMax` legacy module to a very small residual bucket

### Remaining
- move final legacy doctypes (`Credit Details`, `Documents`) into proper module homes
- document final ownership of each module
- clean remaining historical leftovers carefully without breaking imports

## Phase 2: Sales and Billing Foundation

### Completed
- recurring configuration on `Sales Invoice`
- helper for generating next recurring invoice
- customer print and retention defaults
- company print defaults
- WhatsApp and Email PDF send actions
- timeline-based send history
- duplicate-send warning checks

### Next
- scheduled recurring invoice generation
- recurring invoice dashboard / due list
- explicit send history dialog on invoice
- stronger resend rule configuration
- transport delivery fields and workflow for Sales Invoice

## Phase 3: Printings and Document Output

### Completed
- dedicated `Printings` module
- `PDF Settings` moved into `Printings`
- company print defaults
- customer print overrides mapped through customer master and invoice

### Next
- build advanced Jinja print execution using:
  - invoice table format
  - invoice wording
  - customer terms and conditions
  - retention wording
  - letterhead rules
  - language rules
- document-type specific print policy matrix
- customer-specific output styles for special billing requirements
- print/send communication templates by channel

## Phase 4: Expense Management and Cost Attribution

### Completed
- expense types and company account mapping
- budget tracking fields
- employee claim support
- company expense support
- petty cash support
- daily wages support
- approval/payment release fields
- project/customer/service-item cost attribution

### Next
- explicit approval workflow actions
- petty cash settlement workflow
- payment release action and accounting linkage
- expense profitability and budget reports
- reusable expense cost posting patterns into project/service analysis

## Phase 5: Project Management

### Completed
- dedicated `Project Management` module
- project and project service moved cleanly
- contract-oriented project foundation exists

### Next
- project lifecycle stages beyond basic status
- support for maintenance projects
- support for construction projects
- support for vehicle/service operations
- support for third-party contract handling
- project profitability report
- actual cost vs billed amount report
- project overhead and field expense rollups

## Phase 6: Reporting

### Completed
- dedicated `Reporting` module
- reporting standard and reporting standard account structure moved into Reporting

### Next
- report definition doctype
- chart definition doctype
- report filter template doctype
- dashboard cards and chart widgets
- profitability and operational reports by:
  - project
  - customer
  - service item
  - expense type
  - company
- budget vs actual reporting views

## Phase 7: Transport and Operations

### Not Yet Built
This is a major next product track.

### Target Features
- Sales Invoice delivery workflow
- vehicle / driver / route / trip linkage
- third-party carrier handling
- loading and unloading details
- delivery proof / POD
- transport cost capture
- dispatch and invoice linkage
- service profitability by trip / customer / project

## Phase 8: Compliance and Regional Expansion

### Existing Foundation
- E-Invoicing module exists
- ZATCA-related doctypes already exist
- country-aware defaults exist in company setup

### Next
- stronger document-level compliance workflows
- richer country-based form behavior
- multi-country billing and print scenarios
- stronger localized report output

## Phase 9: Product Planning and Delivery Discipline

### Completed
- root project docs now include:
  - `README.md`
  - `SESSION_STATUS.md`
  - `SESSION_CHAT.md`
  - `VISION.md`
  - `ROADMAP.md`

### Next
- add `GAPS.md`
- add `DISCOVERY.md`
- add `BUGS.md`
- create GitHub Project board
- map roadmap phases into issues and cards

## Immediate Priorities

### Priority 1
- advanced print rendering logic
- scheduled recurring invoice generation
- transport delivery workflow on Sales Invoice

### Priority 2
- project profitability reporting
- expense approval and payment release workflow actions
- budget and cost dashboards

### Priority 3
- reporting/chart definition framework
- migration of final old `ERPMax` leftovers
- deeper customer communication templates

## GitHub Project Recommendation

Create a repository project named `ERPMax Product Roadmap` with views for:
- Backlog
- Current
- Bugs
- Modules
- Printing
- Reporting
- Transport

Suggested custom fields:
- Status
- Priority
- Module
- Area
- Phase
- Reference

## Guiding Rule

Every new feature should land in the correct module, document its workflow clearly, and avoid reintroducing the old single-bucket ERPMax structure.
