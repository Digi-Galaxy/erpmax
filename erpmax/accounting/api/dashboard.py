"""ERPMax Dashboard API - Accounting balances, recent vouchers, account breakdown"""
import frappe
from frappe import _
from frappe.query_builder import Criterion, DocType
from frappe.query_builder.functions import Max, Sum
from frappe.utils import cint, flt, nowdate

DEFAULT_RECENT_VOUCHER_LIMIT = 15
MAX_RECENT_VOUCHER_LIMIT = 50
VALID_SCOPES = frozenset({"fy", "all"})
ROOT_TYPES = ("Asset", "Liability", "Equity", "Income", "Expense")


def _first_accessible_company():
    companies = frappe.get_list("Company", pluck="name", order_by="creation asc", limit=1)
    return companies[0] if companies else None


def _resolve_company(company=None):
    company = company.strip() if company else None
    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
    if not company or not frappe.db.exists("Company", company):
        company = _first_accessible_company()
    if not company:
        frappe.throw(_("No company found. Please create a company first."))
    return company


def _normalize_scope(scope=None):
    scope = (scope or "fy").strip().lower()
    if scope not in VALID_SCOPES:
        frappe.throw(_("Unknown scope: {0}").format(scope))
    return scope


def _date_range(company, scope):
    if scope != "fy":
        return None, None
    try:
        from erpnext.accounts.utils import get_fiscal_year
        fy = get_fiscal_year(nowdate(), company=company, as_dict=True)
    except Exception:
        return None, None
    if not fy:
        return None, None
    return str(fy.year_start_date), str(fy.year_end_date)


def _apply_posting_date_range(query, gl_entry, start, end):
    if start:
        query = query.where(gl_entry.posting_date >= start)
    if end:
        query = query.where(gl_entry.posting_date <= end)
    return query


@frappe.whitelist(methods=["GET", "POST"])
def get_balances(company=None, scope="fy"):
    company = _resolve_company(company)
    scope = _normalize_scope(scope)
    start, end = _date_range(company, scope)
    
    gl_entry = DocType("GL Entry")
    account = DocType("Account")
    
    query = (
        frappe.qb.from_(gl_entry)
        .inner_join(account).on(account.name == gl_entry.account)
        .select(
            account.root_type.as_("root_type"),
            Sum(gl_entry.debit).as_("debit"),
            Sum(gl_entry.credit).as_("credit"),
        )
        .where(
            (gl_entry.company == company)
            & (gl_entry.is_cancelled == 0)
            & (account.root_type.isin(ROOT_TYPES))
        )
        .groupby(account.root_type)
    )
    rows = _apply_posting_date_range(query, gl_entry, start, end).run(as_dict=True)
    
    boxes = {rt: 0.0 for rt in ROOT_TYPES}
    for row in rows:
        root_type = row.root_type
        debit = flt(row.debit)
        credit = flt(row.credit)
        if root_type in ("Asset", "Expense"):
            boxes[root_type] = debit - credit
        else:
            boxes[root_type] = credit - debit
    
    return {
        "company": company,
        "scope": scope,
        "date_range": {"start": start, "end": end},
        "boxes": boxes,
        "currency": frappe.get_cached_value("Company", company, "default_currency"),
    }


@frappe.whitelist(methods=["GET", "POST"])
def get_recent_vouchers(company=None, limit=15, scope="fy"):
    company = _resolve_company(company)
    scope = _normalize_scope(scope)
    start, end = _date_range(company, scope)
    limit = max(1, min(cint(limit) or DEFAULT_RECENT_VOUCHER_LIMIT, MAX_RECENT_VOUCHER_LIMIT))
    
    gl_entry = DocType("GL Entry")
    
    voucher_query = (
        frappe.qb.from_(gl_entry)
        .select(
            gl_entry.voucher_type,
            gl_entry.voucher_no,
            Max(gl_entry.posting_date).as_("posting_date"),
            Max(gl_entry.creation).as_("creation"),
        )
        .where((gl_entry.company == company) & (gl_entry.is_cancelled == 0))
        .groupby(gl_entry.voucher_type, gl_entry.voucher_no)
        .orderby(Max(gl_entry.creation), order=frappe.qb.desc)
        .limit(limit)
    )
    vouchers = _apply_posting_date_range(voucher_query, gl_entry, start, end).run(as_dict=True)
    if not vouchers:
        return []
    
    voucher_conditions = [
        (gl_entry.voucher_type == v.voucher_type) & (gl_entry.voucher_no == v.voucher_no)
        for v in vouchers
    ]
    lines = (
        frappe.qb.from_(gl_entry)
        .select(gl_entry.voucher_type, gl_entry.voucher_no, gl_entry.account, gl_entry.debit, gl_entry.credit, gl_entry.is_cancelled)
        .where(
            (gl_entry.company == company) & Criterion.any(voucher_conditions)
        )
        .orderby(gl_entry.debit, order=frappe.qb.desc)
        .run(as_dict=True)
    )
    
    root_map = {}
    for line in lines:
        if line.account not in root_map:
            root_map[line.account] = frappe.db.get_value("Account", line.account, "root_type")
    
    by_voucher = {}
    for line in lines:
        key = (line.voucher_type, line.voucher_no)
        by_voucher.setdefault(key, []).append({
            "account": line.account,
            "root_type": root_map.get(line.account),
            "debit": flt(line.debit),
            "credit": flt(line.credit),
        })
    
    return [
        {
            "voucher_type": v.voucher_type,
            "voucher_no": v.voucher_no,
            "posting_date": str(v.posting_date) if v.posting_date else None,
            "lines": by_voucher.get((v.voucher_type, v.voucher_no), []),
        }
        for v in vouchers
    ]


@frappe.whitelist(methods=["GET", "POST"])
def get_account_breakdown(company, root_type, scope="fy"):
    if root_type not in ROOT_TYPES:
        frappe.throw(_("Unknown root type: {0}").format(root_type))
    
    company = _resolve_company(company)
    scope = _normalize_scope(scope)
    start, end = _date_range(company, scope)
    
    gl_entry = DocType("GL Entry")
    account = DocType("Account")
    
    query = (
        frappe.qb.from_(gl_entry)
        .inner_join(account).on(account.name == gl_entry.account)
        .select(
            gl_entry.account.as_("account"),
            Sum(gl_entry.debit).as_("debit"),
            Sum(gl_entry.credit).as_("credit"),
        )
        .where(
            (gl_entry.company == company)
            & (gl_entry.is_cancelled == 0)
            & (account.root_type == root_type)
            & (account.is_group == 0)
        )
        .groupby(gl_entry.account)
    )
    rows = _apply_posting_date_range(query, gl_entry, start, end).run(as_dict=True)
    
    out = []
    for row in rows:
        debit = flt(row.debit)
        credit = flt(row.credit)
        if root_type in ("Asset", "Expense"):
            balance = debit - credit
        else:
            balance = credit - debit
        if abs(balance) < 0.005:
            continue
        out.append({"account": row.account, "balance": balance})
    
    out.sort(key=lambda a: abs(a["balance"]), reverse=True)
    return out
