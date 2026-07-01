# ERPMax Bugs

## Known Current Bugs / Behavior Risks

### 1. Recurring Invoice Is Manual, Not Scheduled
**Status:** Open

The recurring invoice model exists on `Sales Invoice`, and the next invoice can be generated server-side, but there is no automatic scheduler yet.

**Impact:**
- users must trigger recurring generation manually
- risk of missed recurring invoices

### 2. WhatsApp Send Is Logged As Share Preparation, Not Delivery Confirmation
**Status:** Open / expected limitation

ERPMax can open a WhatsApp share link and log the event in the invoice timeline, but the final send happens outside Frappe.

**Impact:**
- no guaranteed delivery confirmation in-app
- history shows share/open preparation, not recipient read/send confirmation

### 3. Advanced Print Options Are Stored But Not Fully Rendered Yet
**Status:** Open

Fields such as:
- `invoice_table_format`
- `invoice_wording`
- `terms_and_conditions_text`
- customer-specific print overrides

are stored and defaulted, but not yet fully implemented across final Jinja print outputs.

**Impact:**
- data exists but output behavior is still partial
- business may expect more visible formatting differences than currently rendered

### 4. Final Legacy Doctypes Still Remain In Old `ERPMax`
**Status:** Open

Still remaining in the legacy module bucket:
- `Credit Details`
- `Documents`

**Impact:**
- module cleanup is not fully complete
- ownership of those doctypes is still unresolved

### 5. Send History Uses Timeline Comments Only
**Status:** Open design tradeoff

This is intentional, but means send history depends on structured timeline comments rather than a formal send-log doctype.

**Impact:**
- good for audit trail with no extra flags
- future analytics/reporting on send history will need comment parsing or a later dedicated log model

### 6. Expense Workflow Has Data Model But Not Full Action Layer
**Status:** Open

Expense approval/payment release fields exist, but the full approve/reject/release process is not yet implemented as a formal action workflow.

**Impact:**
- user can store workflow data
- process control is not yet complete

### 7. Project Management Is Structurally Present But Operationally Incomplete
**Status:** Open

Project and Project Service exist, but maintenance, construction, fleet, and third-party contract flows are not fully built.

**Impact:**
- project structure is usable
- operational lifecycle still incomplete

### 8. Transport Workflow Is Not Yet Added To Sales Invoice
**Status:** Open

The transport-related delivery workflow discussed earlier is not yet implemented.

**Impact:**
- dispatch and delivery tracking still external/manual
- no full transport cost and delivery traceability yet

## Low-Level Migration / Structure Risks

### 9. Compatibility Wrappers Must Stay Stable During Cleanup
**Status:** Ongoing risk

Old import paths are still being supported through wrapper files.

**Impact:**
- deleting wrappers too early could break imports or migrations
- cleanup should be deliberate and verified

### 10. Customer Print Mapping Needs Template Enforcement
**Status:** Open

Customer and company print defaults now exist, but must be enforced consistently in print rendering and communication actions.

**Impact:**
- defaults may exist in data without full visual effect until templates are completed

## Recommended Bug / Risk Tracking Priorities
1. recurring scheduler gap
2. advanced print rendering mismatch
3. transport workflow missing
4. final module cleanup for residual legacy doctypes
5. full expense action workflow
