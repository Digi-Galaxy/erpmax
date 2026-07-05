# ERPMax — Cross-Session Discoveries

## Frappe v15 Specifics
- **SI Item**: uses `item_name` (Data), not `item_code`. Lookup by `{"item_name": item.item_name}`
- **Account autoname**: `field:account_name` — the account_name IS the document name. Name must include `-ABBR` suffix
- **Account company**: Root accounts (Asset, Liability, Income, Expense) have `company=NULL` on this site
- **Company abbreviation**: Field is `abbreviation`, not `abbr`
- **submit()**: Commits automatically; need explicit `frappe.db.commit()` for script persistence
- **validate_parent_company**: Checks `parent.company != self.company` — both must match (or both be NULL)

## CT Engine Patterns
- **ensure_account**: For auto-creating accounts when rule has no account set. Uses ACCOUNT_NAME_TEMPLATES by (effect, direction). Must handle autoname=field:account_name.
- **_find_parent**: Needs 3-step fallback: matching company → NULL company → any group account
- **Commission GL**: Dr = expense account, Cr = agent's payable account. The agent lookup happens in get_gl_entries_for_term, not in split functions.

## VPS Operations
- **ssh push**: `sudo -u dg bash -c 'cd /home/dg/frappe-bench/apps/erpmax && git push origin develop'`
- **restart**: `sudo supervisorctl restart dg-b16-web:dg-b16-frappe-web`
- **cache**: `bench --site erpmax.celtcoksa.com clear-cache`
- **script pattern**: Write .py locally, scp to VPS, run as dg user

## Repo Structure Notes
- `Taxation` is listed in `modules.txt`, but the current source scan does not show a dedicated `erpmax/taxation/` directory.
- Tree view scripts should follow the app-root layout: module folders like `accounting/` and `inventory/` are rooted under the app, while the core package uses `erpmax/`.
- A doctype folder can exist without being importable during migrate if it is missing `__init__.py`.

## Go Services Notes
- The Go service layer compiles after adding the missing Redis and WebSocket dependencies.
- The Python wrapper in `erpmax/utils/go_services_client.py` is the integration point; ERPMax is not yet auto-routing desk actions through Go services.
- Go list-view queries need both filter args and pagination args passed through; otherwise the SQL path breaks.

## Control Room Notes
- Control Room can safely use Go dashboard data first and keep Frappe fallback for status/activity data.

## List View / Report Builder Notes
- Frappe-facing list view and report-view calls can be routed through a thin client bridge with fallback to native Frappe handlers.
- Report Builder can stay fast by trying Go first and falling back to local `execute()` modules for the report types that are not yet in Go.

## Planning Notes
- Sales Register = posted sales invoice register.
- Purchase Register = posted purchase invoice register.
