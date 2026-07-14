import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, add_months, add_years, getdate

class Subscription(Document):
    def validate(self):
        self.validate_plans()
        self.set_status()

    def validate_plans(self):
        if not self.plans:
            frappe.throw("At least one plan is required")

    def set_status(self):
        today = getdate(nowdate())
        if self.status == "Cancelled":
            return
        if self.end_date and getdate(self.end_date) < today:
            self.status = "Completed"
            return
        if self.trial_period_end and getdate(self.trial_period_end) >= today:
            self.status = "Trialling"
            return
        if self.status not in ("Cancelled", "Completed"):
            self.status = "Active"

    def generate_invoice(self, posting_date=None):
        if self.status in ("Cancelled", "Completed"):
            return None

        pd = getdate(posting_date or nowdate())

        if self.trial_period_end and getdate(self.trial_period_end) >= pd:
            discount_percent = 100
        else:
            discount_percent = 0

        si = frappe.new_doc("Sales Invoice")
        si.customer = self.customer
        si.company = self.company
        si.posting_date = pd
        si.due_date = add_days(pd, self.days_until_due or 0)

        for plan_row in self.plans:
            plan = frappe.get_cached_doc("Subscription Plan", plan_row.plan)
            qty = plan_row.qty or 1
            rate = plan.cost
            if discount_percent:
                rate = rate * (100 - discount_percent) / 100
            si.append("items", {
                "item_name": plan.item_name or plan.plan_name,
                "qty": qty,
                "rate": rate,
                "amount": qty * rate,
            })

        si.flags.ignore_permissions = True
        si.insert()

        if self.submit_invoice and not discount_percent:
            si.submit()

        self.append("invoices", {
            "invoice": si.name,
            "posting_date": pd,
            "amount": si.grand_total,
            "status": si.status,
        })
        self.save(ignore_permissions=True)
        return si.name


def process_all_subscriptions():
    today = getdate(nowdate())
    subs = frappe.get_all("Subscription", filters={
        "status": ["in", ["Active", "Trialling"]],
    })
    created = []
    for sub_data in subs:
        sub_name = sub_data.name
        try:
            sub = frappe.get_doc("Subscription", sub_name)
            if sub.status in ("Cancelled", "Completed"):
                continue
            if sub.cancel_at_period_end and sub.end_date and getdate(sub.end_date) <= today:
                sub.status = "Cancelled"
                sub.save(ignore_permissions=True)
                continue
            if sub.end_date and getdate(sub.end_date) < today:
                sub.status = "Completed"
                sub.save(ignore_permissions=True)
                continue

            # Determine if we need to generate
            needs_generation = False
            if sub.generate_invoice_at == "Beginning of the current subscription period":
                # Check if there are no invoices yet
                if not sub.invoices:
                    needs_generation = True
                else:
                    needs_generation = False
            else:
                # End of period - generate if no invoices yet or last invoice period ended
                if not sub.invoices:
                    needs_generation = True

            if needs_generation:
                inv = sub.generate_invoice(posting_date=today)
                if inv:
                    created.append(inv)
        except Exception as e:
            frappe.log_error("Subscription Error for {}: {}".format(sub_name, str(e)))
    return created
