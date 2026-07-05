import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

from erpmax.utils.naming import sync_transaction_party_fields


class PurchaseInvoice(Document):
    def autoname(self):
        from erpmax.utils.naming import autoname_transaction
        autoname_transaction(self)

    def validate(self):
        sync_transaction_party_fields(self)
        self.calculate_totals()
        self.validate_items()
        self.validate_party()
        self.validate_dates()
        self.set_accounts()
        self.calculate_discount()
        self.calculate_withholding_tax()

    def calculate_totals(self):
        self.total = 0
        for row in self.items:
            if row.qty and row.rate:
                row.amount = row.qty * row.rate
            self.total += row.amount or 0

        self.tax_total = 0
        for row in self.taxes:
            if row.charge_type == "On Net Total" and row.rate:
                row.tax_amount = (self.total * row.rate) / 100
            self.tax_total += row.tax_amount or 0

        self.grand_total = self.total + self.tax_total

        if not self.outstanding_amount or self.docstatus == 0:
            self.outstanding_amount = self.grand_total

        if not self.base_grand_total:
            self.base_grand_total = self.grand_total

    def validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required")

        for row in self.items:
            if not row.item_name:
                frappe.throw(f"Row #{row.idx}: Item Name is required")
            if not row.qty or row.qty <= 0:
                frappe.throw(f"Row #{row.idx}: Quantity must be greater than 0")
            if not row.rate or row.rate < 0:
                frappe.throw(f"Row #{row.idx}: Rate must be 0 or greater")

    def validate_party(self):
        if not self.supplier:
            frappe.throw("Supplier is required")

        supplier = frappe.get_cached_doc("Supplier", self.supplier)
        if supplier.disabled:
            frappe.throw(f"Supplier {self.supplier} is disabled")

    def validate_dates(self):
        if self.due_date and self.posting_date:
            if getdate(self.due_date) < getdate(self.posting_date):
                frappe.throw("Due Date cannot be before Posting Date")

        self.check_overdue()

    def check_overdue(self):
        if self.docstatus == 1 and self.outstanding_amount > 0:
            if self.due_date and getdate(nowdate()) > getdate(self.due_date):
                self.status = "Overdue"
            elif self.outstanding_amount < self.grand_total:
                self.status = "Partly Paid"
            elif self.outstanding_amount <= 0:
                self.status = "Paid"
            else:
                self.status = "Submitted"

    def set_accounts(self):
        if not self.payable_account:
            self.payable_account = self._get_supplier_payable_account()

        if not self.expense_account:
            self.expense_account = self._get_default_expense_account()

        if not self.cost_center:
            self.cost_center = self._get_default_cost_center()

    def _get_supplier_payable_account(self):
        try:
            supplier = frappe.get_cached_doc("Supplier", self.supplier)
            if supplier.default_payable_account:
                return supplier.default_payable_account
        except Exception:
            pass

        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_payable_account'):
            return company.default_payable_account

        account = frappe.db.get_value("Account", {
            "company": self.company,
            "account_type": "Payable",
            "is_group": 0
        }, "name")
        return account

    def _get_default_expense_account(self):
        for item in self.items:
            if item.expense_account:
                return item.expense_account

        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_expense_account'):
            return company.default_expense_account

        account = frappe.db.get_value("Account", {
            "company": self.company,
            "account_type": "Expense",
            "is_group": 0
        }, "name")
        return account

    def _get_default_cost_center(self):
        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'cost_center'):
            return company.cost_center
        return None

    def calculate_discount(self):
        self.discount_amount = 0
        if hasattr(self, 'additional_discount_percentage') and self.additional_discount_percentage:
            self.discount_amount = (self.grand_total * self.additional_discount_percentage) / 100
            self.grand_total -= self.discount_amount
            self.outstanding_amount = self.grand_total

    def calculate_withholding_tax(self):
        self.total_withholding_tax = 0
        if hasattr(self, 'apply_withholding_tax') and self.apply_withholding_tax:
            supplier = frappe.get_cached_doc("Supplier", self.supplier)
            if hasattr(supplier, 'tax_withholding_category') and supplier.tax_withholding_category:
                wht_rate = frappe.db.get_value("Tax Withholding Category",
                    supplier.tax_withholding_category, "rate") or 0
                self.total_withholding_tax = (self.total * wht_rate) / 100
                self.grand_total -= self.total_withholding_tax
                self.outstanding_amount = self.grand_total

    def on_submit(self):
        self.check_overdue()
        self.make_gl_entries()
        self.update_stock()
        self.make_booking_entries()

    def on_cancel(self):
        self.status = "Cancelled"
        self.make_reverse_gl_entries()
        self.revert_stock()
        self.revert_booking_entries()
        self.revert_outstanding()

    def make_gl_entries(self):
        entries = []

        if self.payable_account:
            entries.append({
                "account": self.payable_account,
                "debit": 0,
                "credit": self.grand_total,
                "party_type": "Supplier",
                "party": self.supplier,
            })

        if self.expense_account:
            entries.append({
                "account": self.expense_account,
                "debit": self.total,
                "credit": 0,
            })

        for tax in self.taxes:
            if tax.account_head:
                entries.append({
                    "account": tax.account_head,
                    "debit": tax.tax_amount,
                    "credit": 0,
                })

        if self.total_withholding_tax and self.total_withholding_tax > 0:
            wht_account = self._get_withholding_tax_account()
            if wht_account:
                entries.append({
                    "account": wht_account,
                    "debit": 0,
                    "credit": self.total_withholding_tax,
                    "party_type": "Supplier",
                    "party": self.supplier,
                })

        if self.discount_amount and self.discount_amount > 0:
            discount_account = self._get_discount_account()
            if discount_account:
                entries.append({
                    "account": discount_account,
                    "debit": self.discount_amount,
                    "credit": 0,
                })

        for entry in entries:
            gl = frappe.get_doc({
                "doctype": "GL Entry",
                "company": self.company,
                "posting_date": self.posting_date,
                "account": entry["account"],
                "debit": entry.get("debit", 0),
                "credit": entry.get("credit", 0),
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "party_type": entry.get("party_type"),
                "party": entry.get("party"),
                "cost_center": entry.get("cost_center") or self.cost_center,
            })
            gl.flags.ignore_permissions = True
            gl.insert()

    def _get_withholding_tax_account(self):
        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_withholding_tax_account'):
            return company.default_withholding_tax_account

        account = frappe.db.get_value("Account", {
            "company": self.company,
            "account_type": "Liability",
            "is_group": 0,
            "account_name": ["like", "%Withholding%"]
        }, "name")
        return account

    def _get_discount_account(self):
        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_discount_account'):
            return company.default_discount_account

        account = frappe.db.get_value("Account", {
            "company": self.company,
            "account_type": "Expense",
            "is_group": 0,
            "account_name": ["like", "%Discount%"]
        }, "name")
        return account

    def make_reverse_gl_entries(self):
        existing = frappe.get_all("GL Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for gle in existing:
            frappe.db.set_value("GL Entry", gle.name, "is_cancelled", 1)

    def update_stock(self):
        for item in self.items:
            if hasattr(item, 'item_code') and item.item_code:
                self._update_stock_ledger(item, "in")

    def _update_stock_ledger(self, item, movement_type):
        try:
            warehouse = self._get_receiving_warehouse()
            if not warehouse:
                return

            sle = frappe.get_doc({
                "doctype": "Stock Ledger Entry",
                "item_code": item.item_code,
                "warehouse": warehouse,
                "posting_date": self.posting_date,
                "posting_time": "00:00:00",
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "actual_qty": item.qty if movement_type == "in" else -item.qty,
                "qty_after_transaction": 0,
                "valuation_rate": item.rate or 0,
            })
            sle.flags.ignore_permissions = True
            sle.insert()
        except Exception:
            pass

    def _get_receiving_warehouse(self):
        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_warehouse'):
            return company.default_warehouse

        warehouse = frappe.db.get_value("Warehouse", {
            "company": self.company,
            "is_group": 0
        }, "name")
        return warehouse

    def revert_stock(self):
        existing = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_type": self.doctype,
            "voucher_no": self.name,
        })
        for sle in existing:
            frappe.db.set_value("Stock Ledger Entry", sle.name, "is_cancelled", 1)

    def make_booking_entries(self):
        pass

    def revert_booking_entries(self):
        pass

    def revert_outstanding(self):
        self.outstanding_amount = self.grand_total
        self.status = "Submitted"
        self.db_update()

    def get_payments_made(self):
        filters = {
            "reference_doctype": "Purchase Invoice",
            "reference_name": self.name,
            "docstatus": 1,
        }

        paid = frappe.db.get_value(
            "Payment Entry Reference",
            filters,
            "sum(allocated_amount)",
        ) or 0

        return paid

    @frappe.whitelist()
    def create_debit_note(self):
        try:
            dn = frappe.get_doc({
                "doctype": "Purchase Invoice",
                "supplier": self.supplier,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 30),
                "company": self.company,
                "is_return": 1,
                "return_against": self.name,
                "items": [{
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": -item.qty,
                    "rate": item.rate,
                    "amount": -item.amount,
                    "expense_account": item.expense_account,
                } for item in self.items],
                "taxes": [{
                    "charge_type": tax.charge_type,
                    "account_head": tax.account_head,
                    "rate": tax.rate,
                    "tax_amount": -tax.tax_amount,
                    "description": tax.description,
                } for tax in self.taxes],
            })
            dn.insert()
            return dn.name
        except Exception as e:
            frappe.throw(f"Failed to create debit note: {str(e)}")

    @frappe.whitelist()
    def create_payment(self):
        try:
            pe = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Pay",
                "party_type": "Supplier",
                "party": self.supplier,
                "posting_date": nowdate(),
                "company": self.company,
                "paid_amount": self.outstanding_amount,
                "received_amount": self.outstanding_amount,
                "paid_from": self.payable_account,
                "paid_to": self._get_bank_account(),
                "references": [{
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": self.name,
                    "total_amount": self.grand_total,
                    "outstanding_amount": self.outstanding_amount,
                    "allocated_amount": self.outstanding_amount,
                }],
            })
            pe.insert()
            return pe.name
        except Exception as e:
            frappe.throw(f"Failed to create payment entry: {str(e)}")

    def _get_bank_account(self):
        company = frappe.get_cached_doc("Company", self.company)
        if hasattr(company, 'default_bank_account'):
            return company.default_bank_account

        account = frappe.db.get_value("Account", {
            "company": self.company,
            "account_type": "Bank",
            "is_group": 0
        }, "name")
        return account

    @frappe.whitelist()
    def get_account_balance(self, account=None):
        if not account:
            account = self.payable_account
        if not account:
            return 0

        result = frappe.db.get_value("GL Entry", {
            "account": account,
            "party_type": "Supplier",
            "party": self.supplier,
            "company": self.company,
            "is_cancelled": 0,
        }, ["sum(debit)", "sum(credit)"])

        debit = result[0] or 0
        credit = result[1] or 0
        return debit - credit

    @frappe.whitelist()
    def get_supplier_outstanding(self):
        result = frappe.db.get_value("GL Entry", {
            "party_type": "Supplier",
            "party": self.supplier,
            "company": self.company,
            "is_cancelled": 0,
        }, ["sum(debit)", "sum(credit)"])

        debit = result[0] or 0
        credit = result[1] or 0
        return credit - debit
