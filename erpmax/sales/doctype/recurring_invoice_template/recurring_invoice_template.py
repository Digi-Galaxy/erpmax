import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, add_months, get_first_day, get_last_day
from datetime import datetime


class RecurringInvoiceTemplate(Document):
    def validate(self):
        self.calculate_total()
        if not self.next_invoice_date and self.start_date:
            self.next_invoice_date = self.start_date

    def calculate_total(self):
        total = 0
        for item in self.items:
            item.amount = (item.qty or 0) * (item.rate or 0)
            total += item.amount
        self.total = total

    def generate_invoice(self):
        """Generate Sales Invoice from this template"""
        if not self.enabled:
            frappe.throw("Template is disabled")

        if self.end_date and self.next_invoice_date > self.end_date:
            frappe.throw("Template has expired")

        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": self.company,
            "customer": self.customer,
            "posting_date": today(),
            "due_date": add_days(today(), 30),
            "recurring_invoice_template": self.name,
            "notes": f"Generated from Recurring Invoice Template: {self.template_name}\n{self.notes or ''}"
        })

        for item in self.items:
            invoice.append("items", {
                "item": item.item,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": item.amount
            })

        invoice.flags.ignore_permissions = True
        invoice.insert()

        if self.auto_submit:
            invoice.submit()

        self.update_next_invoice_date()

        return invoice.name

    def update_next_invoice_date(self):
        """Update next invoice date based on frequency"""
        if self.frequency == "Daily":
            self.next_invoice_date = add_days(self.next_invoice_date, 1)
        elif self.frequency == "Weekly":
            self.next_invoice_date = add_days(self.next_invoice_date, 7)
        elif self.frequency == "Monthly":
            self.next_invoice_date = add_months(self.next_invoice_date, 1)
            if self.repeat_on_day:
                try:
                    next_date = datetime.strptime(str(self.next_invoice_date), "%Y-%m-%d")
                    day = min(int(self.repeat_on_day), 28)
                    self.next_invoice_date = next_date.replace(day=day).strftime("%Y-%m-%d")
                except:
                    pass
        elif self.frequency == "Quarterly":
            self.next_invoice_date = add_months(self.next_invoice_date, 3)
        elif self.frequency == "Yearly":
            self.next_invoice_date = add_months(self.next_invoice_date, 12)

        self.save()


def process_recurring_invoices():
    """Background job to process all recurring invoice templates"""
    templates = frappe.get_all(
        "Recurring Invoice Template",
        filters={
            "enabled": 1,
            "next_invoice_date": ["<=", today()]
        },
        fields=["name"]
    )

    created_invoices = []
    for template_name in templates:
        try:
            template = frappe.get_doc("Recurring Invoice Template", template_name.name)
            if template.end_date and template.next_invoice_date > template.end_date:
                template.enabled = 0
                template.save()
                continue

            invoice_name = template.generate_invoice()
            created_invoices.append(invoice_name)
        except Exception as e:
            frappe.log_error(f"Failed to generate invoice for template {template_name.name}: {str(e)}")

    return created_invoices


def create_recurring_invoice(template_name):
    """Manual trigger to create invoice from template"""
    template = frappe.get_doc("Recurring Invoice Template", template_name)
    return template.generate_invoice()
