import frappe
from frappe.model.document import Document

from erpmax.utils.naming import sync_transaction_party_fields

class ProformaInvoice(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)


    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()

    def calculate_totals(self):
        self.total = sum((row.amount or 0) for row in self.items)
        self.tax_total = sum((row.tax_amount or 0) for row in self.taxes)
        self.grand_total = self.total + self.tax_total
        self.outstanding_amount = self.grand_total

    def on_submit(self):
        if self.sales_invoice and frappe.db.exists("Sales Invoice", self.sales_invoice):
            return

        sales_invoice = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "posting_date": self.posting_date,
                "company": self.company,
                "due_date": self.due_date,
                "proforma_invoice": self.name,
                "items": [
                    {
                        "item_name": row.item_name,
                        "description": row.description,
                        "qty": row.qty,
                        "rate": row.rate,
                        "amount": row.amount,
                        "income_account": row.income_account,
                        "uom": row.uom,
                    }
                    for row in (self.items or [])
                ],
                "taxes": [
                    {
                        "charge_type": row.charge_type,
                        "account_head": row.account_head,
                        "rate": row.rate,
                        "tax_amount": row.tax_amount,
                        "description": row.description,
                    }
                    for row in (self.taxes or [])
                ],
            }
        )
        sales_invoice.flags.ignore_permissions = True
        sales_invoice.insert()
        self.sales_invoice = sales_invoice.name
        self.status = "Converted"
        frappe.db.set_value(self.doctype, self.name, "sales_invoice", sales_invoice.name, update_modified=False)
        frappe.db.set_value(self.doctype, self.name, "status", "Converted", update_modified=False)

    def on_cancel(self):
        self.status = "Cancelled"

