import frappe
from frappe.model.document import Document
from frappe.utils import add_days, add_years, getdate, nowdate


class FiscalYear(Document):
    def validate(self):
        if not self.fiscal_year_name:
            self.fiscal_year_name = self.fiscal_year
        if not self.fiscal_year:
            self.fiscal_year = self.fiscal_year_name


def _get_fiscal_year_rows():
    return frappe.get_all(
        "Fiscal Year",
        fields=["name", "fiscal_year_name", "year_start_date", "year_end_date"],
        order_by="year_start_date asc, year_end_date asc",
    )


def _overlaps_existing_year(start_date, end_date, rows):
    for row in rows:
        if not row.year_start_date or not row.year_end_date:
            continue
        existing_start = getdate(row.year_start_date)
        existing_end = getdate(row.year_end_date)
        if existing_start <= end_date and existing_end >= start_date:
            return row
    return None


@frappe.whitelist()
def auto_create_fiscal_year():
    today = getdate(nowdate())
    rows = _get_fiscal_year_rows()

    for row in rows:
        if not row.year_start_date or not row.year_end_date:
            continue
        start_date = getdate(row.year_start_date)
        end_date = getdate(row.year_end_date)
        if start_date <= today <= end_date:
            return {"created": False, "reason": "current fiscal year exists", "name": row.name}

    future_years = [row for row in rows if row.year_start_date and getdate(row.year_start_date) > today]
    if future_years:
        next_year = future_years[0]
        return {"created": False, "reason": "future fiscal year already exists", "name": next_year.name}

    latest = None
    for row in rows:
        if not row.year_end_date:
            continue
        if latest is None or getdate(row.year_end_date) > getdate(latest.year_end_date):
            latest = row

    if latest and latest.year_end_date:
        start_date = add_days(getdate(latest.year_end_date), 1)
    else:
        start_date = getdate(f"{today.year}-01-01")

    end_date = add_days(add_years(start_date, 1), -1)
    overlapping = _overlaps_existing_year(start_date, end_date, rows)
    if overlapping:
        return {
            "created": False,
            "reason": "overlapping fiscal year exists",
            "name": overlapping.name,
        }

    fiscal_year_name = f"{start_date.year}-{end_date.year}"
    if frappe.db.exists("Fiscal Year", fiscal_year_name):
        return {"created": False, "reason": "fiscal year exists", "name": fiscal_year_name}

    doc = frappe.get_doc({
        "doctype": "Fiscal Year",
        "fiscal_year_name": fiscal_year_name,
        "fiscal_year": fiscal_year_name,
        "year_start_date": start_date,
        "year_end_date": end_date,
        "time_span": "Long Year",
        "is_short_year": 0,
    })
    doc.insert(ignore_permissions=True)
    return {"created": True, "name": doc.name, "start_date": str(start_date), "end_date": str(end_date)}
