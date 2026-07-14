import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_months, add_days


def process_all_auto_invoices():
    """Scheduled job: generate invoices for all auto-invoice contracts"""
    process_service_contracts()
    process_rental_contracts()
    process_employee_contracts()


def process_service_contracts():
    contracts = frappe.get_all(
        "Service Contract",
        filters={
            "current_stage": "Active",
            "auto_invoice": 1,
            "billing_cycle": ["in", ["Monthly", "Quarterly", "Yearly"]],
        },
        fields=["name", "billing_cycle", "last_invoiced_date", "start_date"],
    )

    today = getdate()

    for contract in contracts:
        if should_generate(contract, today):
            try:
                doc = frappe.get_doc("Service Contract", contract.name)
                doc.generate_invoice(posting_date=str(today))
                frappe.db.commit()
            except Exception as e:
                frappe.db.rollback()
                frappe.log_error(f"Auto-invoice failed for Service Contract {contract.name}: {str(e)}")


def process_rental_contracts():
    contracts = frappe.get_all(
        "Rental Contract",
        filters={
            "current_stage": "Active",
            "auto_invoice": 1,
            "billing_cycle": ["in", ["Monthly"]],
        },
        fields=["name", "billing_cycle", "last_invoiced_date", "start_date"],
    )

    today = getdate()

    for contract in contracts:
        if should_generate(contract, today):
            try:
                doc = frappe.get_doc("Rental Contract", contract.name)
                doc.generate_invoice(posting_date=str(today))
                frappe.db.commit()
            except Exception as e:
                frappe.db.rollback()
                frappe.log_error(f"Auto-invoice failed for Rental Contract {contract.name}: {str(e)}")


def process_employee_contracts():
    contracts = frappe.get_all(
        "Employee Contract",
        filters={
            "current_stage": "Active",
            "auto_invoice": 1,
            "billing_cycle": ["in", ["Monthly"]],
        },
        fields=["name", "billing_cycle", "last_invoiced_date", "start_date"],
    )

    today = getdate()

    for contract in contracts:
        if should_generate(contract, today):
            try:
                doc = frappe.get_doc("Employee Contract", contract.name)
                doc.generate_invoice(posting_date=str(today))
                frappe.db.commit()
            except Exception as e:
                frappe.db.rollback()
                frappe.log_error(f"Auto-invoice failed for Employee Contract {contract.name}: {str(e)}")


def should_generate(contract, today):
    """Determine if invoice should be generated based on billing cycle"""
    if not contract.last_invoiced_date:
        return True

    last = getdate(contract.last_invoiced_date)
    cycle = contract.billing_cycle

    if cycle == "Monthly":
        next_date = add_months(last, 1)
    elif cycle == "Quarterly":
        next_date = add_months(last, 3)
    elif cycle == "Yearly":
        next_date = add_months(last, 12)
    else:
        return False

    if not contract.start_date:
        return today >= next_date

    start = getdate(contract.start_date)
    return today >= next_date and today >= start
