# ERPMax Gaps

## Current Gaps by Area

### Sales
- no automatic recurring invoice scheduler yet
- no recurring dashboard / due queue
- no send-history dialog on Sales Invoice
- no transport delivery fields/workflow yet
- no integrated delivery proof / POD handling yet
- no route / trip / driver / vehicle linkage yet

### Printings
- advanced print template execution is not yet complete
- invoice table format choices are stored but not yet fully rendered through print templates
- customer wording and terms are stored but not yet fully consumed across all print outputs
- no print policy matrix by doctype/channel/customer class yet

### Reporting
- no report definition doctype yet
- no chart definition doctype yet
- no filter template doctype yet
- no profitability dashboards yet
- no budget dashboard yet
- no reporting workspace/cards/charts yet

### Project Management
- project lifecycle is still basic
- no structured maintenance workflow yet
- no construction workflow yet
- no fleet/vehicle service workflow yet
- no third-party contract workflow yet
- no project profitability dashboard yet

### Expense Management
- no explicit approve/reject/release payment action layer yet
- no petty cash settlement process yet
- no payment posting automation yet
- no standard expense budget report yet
- no project/service expense profitability report yet

### Commerce
- residual doctypes still remain outside their final homes
- customer-specific communication templates are not yet formalized
- credit and commercial exception handling still needs cleanup

### Legacy Cleanup
Remaining old `ERPMax` doctypes:
- `Credit Details`
- `Documents`

## Risk Areas
- module split must keep compatibility wrappers until the codebase is fully cleaned
- send-history is good, but print/send UI still needs a stronger review screen
- recurring generation exists manually/server-side but not yet automatically scheduled
- customer print rules exist in data but not yet fully enforced in print rendering

## Highest Priority Gaps
1. automatic recurring invoice generation
2. transport workflow on Sales Invoice
3. advanced print rendering based on customer/company settings
4. project and service profitability reporting
5. expense approval/payment action layer
6. final module cleanup
