import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days

from erpmax.utils.naming import sync_transaction_party_fields
from erpmax.service_management.utils.flow import set_stage, get_allowed_stages


class EmployeeContract(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.validate_dates()
        if not self.current_stage:
            self.current_stage = "Draft"

    def validate_dates(self):
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(_("End Date cannot be before Start Date"))

    @frappe.whitelist()
    def set_stage(self, to_stage, notes=None):
        set_stage(self, to_stage, notes=notes)
        return {"current_stage": self.current_stage}

    @frappe.whitelist()
    def get_allowed_stages(self):
        return get_allowed_stages(self.doctype, self.current_stage)

    @frappe.whitelist()
    def generate_invoice(self, posting_date=None):
        if self.current_stage != "Active":
            frappe.throw(_("Only Active contracts can generate invoices"))

        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer,
            "posting_date": posting_date or nowdate(),
            "due_date": add_days(posting_date or nowdate(), 30),
            "company": self.company,
            "service_contract": self.name,
            "contract_type": "Employee",
            "items": [
                {
                    "item_name": f"{self.employee_name} - {self.designation or 'Services'}",
                    "description": f"Employee Contract: {self.employee_name}, Designation: {self.designation or 'N/A'}, Period: {(posting_date or nowdate())}",
                    "qty": 1,
                    "rate": self.monthly_rate or 0,
                    "amount": self.monthly_rate or 0,
                }
            ],
        })
        si.flags.ignore_permissions = True
        si.insert()

        self.last_invoiced_date = posting_date or nowdate()
        self.db_update()

        return si.name

    @frappe.whitelist()
    def generate_pdf(self):
        from erpmax.service_management.utils.pdf_contract import generate_contract_pdf
        return generate_contract_pdf(self.doctype, self.name)
