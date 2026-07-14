import frappe
from frappe import _
from frappe.model.document import Document


class TransactionDeletionRecord(Document):
    def validate(self):
        frappe.only_for("System Manager")

    def on_submit(self):
        self.db_set("status", "Running")
        frappe.enqueue(
            self.start_deletion,
            queue="long",
            job_name=f"delete_transactions_{self.name}",
        )

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def start_deletion(self):
        try:
            progress = []
            company = self.company

            # Define transaction doctypes and their company link fields
            doctypes_to_delete = []

            if self.delete_sales_invoices:
                doctypes_to_delete.append(("Sales Invoice", "company"))
            if self.delete_purchase_invoices:
                doctypes_to_delete.append(("Purchase Invoice", "company"))
            if self.delete_payment_entries:
                doctypes_to_delete.append(("Payment Entry", "company"))
            if self.delete_journal_entries:
                doctypes_to_delete.append(("Journal Entry", "company"))
            if self.delete_gl_entries:
                doctypes_to_delete.append(("GL Entry", "company"))
            if self.delete_purchase_orders:
                doctypes_to_delete.append(("Purchase Order", "company"))
            if self.delete_purchase_receipts:
                doctypes_to_delete.append(("Purchase Receipt", "company"))
            if self.delete_sales_orders:
                doctypes_to_delete.append(("Sales Order", "company"))
            if self.delete_delivery_notes:
                doctypes_to_delete.append(("Delivery Note", "company"))
            if self.delete_stock_entries:
                doctypes_to_delete.append(("Stock Entry", "company"))
            if self.delete_material_requests:
                doctypes_to_delete.append(("Material Request", "company"))
            if self.delete_quotations:
                doctypes_to_delete.append(("Quotation", "company"))
            if self.delete_proj:
                doctypes_to_delete.append(("Project", "customer"))

            for doctype, link_field in doctypes_to_delete:
                if not frappe.db.exists("DocType", doctype):
                    continue

                count = frappe.db.count(doctype, {link_field: company})
                if count == 0:
                    progress.append(f"{doctype}: 0 (skipped)")
                    continue

                # Get all records for this company
                docs = frappe.get_all(doctype, filters={link_field: company}, pluck="name", limit_page_length=0)
                deleted = 0

                for doc_name in docs:
                    try:
                        doc = frappe.get_doc(doctype, doc_name)
                        # Cancel if submitted before deleting
                        if doc.docstatus == 1:
                            doc.cancel()
                        frappe.delete_doc(doctype, doc_name, force=True)
                        deleted += 1
                    except Exception:
                        frappe.db.rollback()
                        continue

                progress.append(f"{doctype}: {deleted}/{count} deleted")

            self.db_set("progress", "\n".join(progress))
            self.db_set("status", "Completed")
            frappe.db.commit()

        except Exception as e:
            self.db_set("status", "Failed")
            self.db_set("error_log", frappe.get_traceback())
            frappe.db.commit()


@frappe.whitelist()
def is_deletion_doc_running(company):
    running = frappe.db.get_all(
        "Transaction Deletion Record",
        filters={"company": company, "status": ("in", ["Running", "Queued"]), "docstatus": 1},
        limit=1,
    )
    if running:
        frappe.throw(
            _("A deletion record {0} is already running for {1}").format(
                running[0].name, company
            )
        )
