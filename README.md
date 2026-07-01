# ERPMax

ERPMax is a modular Frappe ERP focused on accounting, commerce, projects, expense control, printing, e-invoicing, and service-heavy operational workflows.

## Current Module Structure

- `ERPMax`: residual legacy bucket; only `Credit Details` and `Documents` remain
- `Accounting`: charting, journals, payment entry, fiscal year, cost centres, tax templates
- `Business Setup`: company, holiday list, ERPMax settings, employee, expense claim
- `Commerce`: customer, address, VAT process
- `Purchase`: supplier and purchase document flow
- `Sales`: sales invoice flow
- `Expense Management`: expense type and company account-budget mapping
- `Inventory`: item master
- `Project Management`: project and project service
- `Reporting`: reporting standards and account mapping
- `Printings`: PDF and invoice print behavior settings
- `E-Invoicing`: ZATCA-related compliance doctypes

## Key Functional Areas

### Sales and Billing
- Sales Invoice with customer-specific retention defaults
- recurring invoice setup on invoice itself
- server-side next recurring invoice generator
- customer-specific print format, print heading, wording, language, and terms
- WhatsApp print share and email PDF send actions with duplicate-send warnings
- timeline-based send history without extra sent-status fields

### Expense Management
- employee expense claims
- company expense claims
- petty cash claims
- daily wages / food / field expense scenarios
- approval and payment release fields
- budget vs actual tracking per company + expense type + account
- project / customer / service cost attribution on expense rows

### Projects
- project master with contract-oriented fields
- service rows under projects
- foundation for maintenance, construction, transport, and third-party contract costing

### Reporting
- reporting standard master
- reporting account structure mapping
- intended base for future charts, dashboards, and generated reports

### Printings
- company-level PDF and print defaults
- customer print override support
- invoice table format and wording support
- letterhead, draft heading, and print repetition options

## Important Design Choices

### No Send-Status Custom Flags
Invoice send history is stored in timeline comments, not extra sent-marker fields. This avoids duplicate status fields while still allowing resend protection.

### Customer-Specific Print Mapping
Different customers may require:
- different retention settings
- different wording
- different terms and conditions
- different invoice table layout
- different print format
- different heading / language / letterhead

Those defaults are stored on `Customer`, with company fallbacks on `PDF Settings`, then applied to `Sales Invoice`.

### Recurring Invoice Model
Recurring behavior is configured directly from the source invoice. The recurring invoice is not on by default. When enabled, the source invoice stores recurrence details and can generate the next draft invoice with copied customer, company, items, and print settings.

## Live Features Already Added

### Sales Invoice Send Actions
- `Send > Email PDF`
- `Send > WhatsApp Print`

### Duplicate Send Guard
Before sending again, ERPMax checks timeline history for:
- same channel
- same recipient
- same print format

If found, ERPMax asks for confirmation before resend.

### Expense Budget Tracking
Each expense row can show:
- budget period
- budget amount
- actual before claim
- actual after claim
- variance
- over-budget indicator

## Current Gaps / Pending Build-Out

### Functional Gaps
- automatic scheduler for recurring invoice generation
- full transport delivery workflow on Sales Invoice
- project lifecycle completion for maintenance / construction / fleet / subcontract scenarios
- reporting dashboards, chart definitions, report definitions, filter templates
- advanced Jinja print templates that fully consume invoice table format and wording controls

### Residual Legacy Doctypes
Still in module `ERPMax`:
- `Credit Details`
- `Documents`

## Reference Sources Used
This project has been aligned using targeted reference review from:
- `E:\Projects\Daftara App`
- `E:\Projects\Manager`
- `E:\library\_ref`
- ERPNext and Frappe references under `E:\library\_ref\erp\erpnext\v16` and `E:\library\_ref\frappe\v16`

The references were used to guide:
- recurring / repeat document patterns
- module separation
- print format behavior
- email attachment flow via `attach_print`
- customer / document defaulting patterns

## Working Notes
- WhatsApp logging records share preparation/opening from ERPMax; final send happens outside Frappe
- Email PDF sending is initiated from ERPMax and logged to the invoice timeline
- terms currently use text fields because the site does not have a native `Terms and Conditions` doctype installed
- compatibility wrappers remain in old paths to reduce breakage during the module transition

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app erpmax
```

## App Root Documents
- `README.md`: project overview and architecture
- `SESSION_STATUS.md`: current delivery state and pending work
- `SESSION_CHAT.md`: copied historical session archive
- `VPS_ACCESS.md`: VPS access reference

## License

mit
