import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class PaymentTerm(Document):
    def validate(self):
        pass


@frappe.whitelist()
def create_payment_schedule(payment_term_name, invoice_date, total_amount):
    from frappe.utils import add_days, getdate
    payment_term = frappe.get_doc("Payment Term", payment_term_name)
    invoice_date = getdate(invoice_date)
    schedule = []
    for detail in payment_term.payment_terms_details:
        due_date = add_days(invoice_date, int(detail.due_date))
        amount = flt(total_amount) * flt(detail.percentage) / 100
        schedule.append({
            "description": detail.description,
            "due_date": due_date,
            "percentage": detail.percentage,
            "amount": flt(amount, 2),
            "status": "Pending"
        })
    return schedule
