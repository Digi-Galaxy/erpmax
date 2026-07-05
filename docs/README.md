# ERPMax Docs

Compact project snapshot for the current ERPMax repo.

## Exists
- `erpmax/` app package with hooks, setup, utilities, fixtures, public assets, and reports.
- Module namespaces in `modules.txt`: `ERPMax`, `Accounting`, `Banking`, `Business Setup`, `Commerce`, `Project Management`, `Inventory`, `Expense Management`, `Purchase`, `Sales`, `Reporting`, `Printings`, `Taxation`.
- Core source areas already present: accounting, banking, business_setup, commerce, project_management, inventory, expense_management, sales, purchase, reporting, printings, stock, and e_invoicing.
- `Taxation` appears in `modules.txt`, but the dedicated source tree is not yet separate in this scan.
- ZATCA-related code exists under `e_invoicing`.

## Not Yet
- Full ERPNext parity across every master doctype.
- A transport module inside this repo.
- Final release and test sign-off.

## Docs Map
- `project/` project intent and working rules.
- `requirements/` feature scope.
- `planning/` roadmap and tasks.
- `planning/FRONTEND_RENDERING_PLAN.md` heavy screen rendering strategy.
- `status/` current status and session logs.
- `audit/` implementation notes.
- `chat_sessions/` compact chat history.
- `audit/COMPARATIVE_AUDIT.md` comparison against other ERPs.
- `REPO_TREE.md` functional repository tree.
