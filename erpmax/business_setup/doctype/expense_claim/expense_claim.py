import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, get_first_day, get_last_day, now_datetime


def get_expense_type_defaults(expense_type, company):
    if not expense_type:
        return {}

    defaults = frappe.db.get_value(
        "Expense Type",
        expense_type,
        ["default_mode_of_payment", "requires_receipt", "is_billable"],
        as_dict=True,
    ) or {}

    if company:
        mapping = frappe.db.get_value(
            "Expense Type Account",
            {
                "parent": expense_type,
                "parenttype": "Expense Type",
                "parentfield": "accounts",
                "company": company,
            },
            ["account", "cost_center", "budget_period", "budget_amount", "budget_alert_percentage"],
            as_dict=True,
        ) or {}
        defaults.update(mapping)

    return defaults


def get_budget_window(posting_date, budget_period):
    if not posting_date or not budget_period:
        return None, None

    if budget_period == "Monthly":
        return get_first_day(posting_date), get_last_day(posting_date)

    if budget_period == "Quarterly":
        month_index = posting_date.month - 1
        quarter_start_month = (month_index // 3) * 3 + 1
        start_date = posting_date.replace(month=quarter_start_month, day=1)
        end_date = get_last_day(add_months(start_date, 2))
        return start_date, end_date

    if budget_period == "Yearly":
        start_date = posting_date.replace(month=1, day=1)
        end_date = posting_date.replace(month=12, day=31)
        return start_date, end_date

    return None, None


def get_actual_expense(company, expense_type, from_date, to_date, current_claim):
    if not all([company, expense_type, from_date, to_date]):
        return 0

    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(COALESCE(ecd.total_amount, COALESCE(ecd.amount, 0) + COALESCE(ecd.tax_amount, 0))), 0)
        FROM `tabExpense Claim Detail` ecd
        INNER JOIN `tabExpense Claim` ec ON ec.name = ecd.parent
        WHERE ec.docstatus = 1
          AND ec.company = %s
          AND ecd.expense_type = %s
          AND ec.posting_date BETWEEN %s AND %s
          AND ec.name != %s
        """,
        (company, expense_type, from_date, to_date, current_claim or ""),
    )
    return result[0][0] if result else 0


class ExpenseClaim(Document):
    def validate(self):
        if self.claim_type == "Employee Claim" and not self.employee:
            frappe.throw(_("Employee is required for Employee Claim."))

        if self.claim_type != "Employee Claim" and not self.beneficiary_name and not self.employee:
            frappe.throw(_("Beneficiary Name is required for non-employee expense claims."))

        if self.paid_amount and self.paid_amount > (self.total_amount or 0):
            frappe.throw(_("Paid Amount cannot be greater than Total Amount."))

    def before_save(self):
        if self.employee and not self.company:
            self.company = frappe.db.get_value("Employee", self.employee, "company")

        if self.employee and not self.beneficiary_name:
            self.beneficiary_name = self.employee_name or frappe.db.get_value("Employee", self.employee, "employee_name")

        expense_total = 0
        tax_total = 0

        for row in self.get("expenses", []):
            row.date = row.date or self.posting_date
            row.project = row.project or self.project
            row.beneficiary_name = row.beneficiary_name or self.beneficiary_name

            defaults = get_expense_type_defaults(row.expense_type, self.company)

            if not self.mode_of_payment and defaults.get("default_mode_of_payment"):
                self.mode_of_payment = defaults.get("default_mode_of_payment")

            qty = row.qty or 1
            row.qty = qty

            if row.rate and not row.amount:
                row.amount = qty * row.rate
            elif row.amount and not row.rate and qty:
                row.rate = row.amount / qty

            if not row.account and defaults.get("account"):
                row.account = defaults.get("account")

            if not row.cost_center:
                row.cost_center = self.cost_center or defaults.get("cost_center")

            if not row.cost_center and row.project:
                row.cost_center = frappe.db.get_value("Project", row.project, "cost_centre")

            if row.project and not row.customer:
                row.customer = frappe.db.get_value("Project", row.project, "customer")

            row.tax_amount = row.tax_amount or 0
            row.total_amount = (row.amount or 0) + row.tax_amount

            if row.is_billable_to_customer and not row.billable_amount:
                row.billable_amount = row.total_amount
            elif not row.is_billable_to_customer:
                row.billable_amount = 0

            budget_period = defaults.get("budget_period")
            budget_amount = defaults.get("budget_amount") or 0
            row.budget_period = budget_period or ""
            row.budget_amount = budget_amount
            row.actual_before_claim = 0
            row.actual_after_claim = row.total_amount
            row.budget_variance = 0
            row.over_budget = 0

            from_date, to_date = get_budget_window(self.posting_date or row.date, budget_period)
            if budget_amount and from_date and to_date:
                actual_before_claim = get_actual_expense(
                    self.company,
                    row.expense_type,
                    from_date,
                    to_date,
                    self.name,
                )
                actual_after_claim = actual_before_claim + row.total_amount
                row.actual_before_claim = actual_before_claim
                row.actual_after_claim = actual_after_claim
                row.budget_variance = budget_amount - actual_after_claim

                alert_percentage = defaults.get("budget_alert_percentage") or 100
                alert_limit = budget_amount * (alert_percentage / 100)
                row.over_budget = 1 if actual_after_claim > alert_limit else 0

            expense_total += row.amount or 0
            tax_total += row.tax_amount or 0

        self.total_tax_amount = tax_total
        self.total_amount = expense_total + tax_total

        if not self.paid_amount:
            self.payment_status = "Unpaid"
        elif self.paid_amount < self.total_amount:
            self.payment_status = "Partly Paid"
        else:
            self.payment_status = "Paid"

        if self.status == "Approved" and not self.approved_on:
            self.approved_on = now_datetime()

    def on_submit(self):
        if self.status in (None, "", "Draft"):
            self.status = "Pending Approval"

    def on_cancel(self):
        self.status = "Cancelled"
