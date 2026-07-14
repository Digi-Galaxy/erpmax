# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate, get_time, time_diff_in_hours


class Timesheet(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_time_logs()
    
    def calculate_totals(self):
        """Calculate total hours and amount"""
        self.total_hours = 0
        self.total_amount = 0
        
        for log in self.time_logs:
            # Calculate hours from time difference
            if log.from_time and log.to_time:
                log.hours = time_diff_in_hours(log.to_time, log.from_time)
            
            # Calculate amount
            if log.hours and log.rate:
                log.amount = flt(log.hours) * flt(log.rate)
            
            self.total_hours += flt(log.hours)
            self.total_amount += flt(log.amount)
    
    def validate_time_logs(self):
        """Validate time log entries"""
        if not self.time_logs:
            frappe.throw(_("At least one time log is required"))
        
        for log in self.time_logs:
            if log.from_time and log.to_time:
                if get_time(log.from_time) >= get_time(log.to_time):
                    frappe.throw(_("Row {0}: From time must be before To time").format(log.idx))
            
            if flt(log.hours) <= 0:
                frappe.throw(_("Row {0}: Hours must be greater than 0").format(log.idx))
    
    def on_submit(self):
        """Actions on submit"""
        self.status = "Submitted"
        self.db_update()
        
        # Update project/task hours if linked
        self.update_project_hours()
    
    def on_cancel(self):
        """Actions on cancel"""
        self.status = "Cancelled"
        self.db_update()
        
        # Reverse project/task hours
        self.reverse_project_hours()
    
    def update_project_hours(self):
        """Update project/task with logged hours"""
        for log in self.time_logs:
            if log.project:
                # Update project total hours
                current_hours = frappe.db.get_value("Project", log.project, "total_hours") or 0
                frappe.db.set_value("Project", log.project, "total_hours", current_hours + flt(log.hours))
            
            if log.task:
                # Update task total hours
                current_hours = frappe.db.get_value("Task", log.task, "total_hours") or 0
                frappe.db.set_value("Task", log.task, "total_hours", current_hours + flt(log.hours))
    
    def reverse_project_hours(self):
        """Reverse project/task hours on cancel"""
        for log in self.time_logs:
            if log.project:
                current_hours = frappe.db.get_value("Project", log.project, "total_hours") or 0
                frappe.db.set_value("Project", log.project, "total_hours", current_hours - flt(log.hours))
            
            if log.task:
                current_hours = frappe.db.get_value("Task", log.task, "total_hours") or 0
                frappe.db.set_value("Task", log.task, "total_hours", current_hours - flt(log.hours))


@frappe.whitelist()
def get_timesheet_summary(employee=None, from_date=None, to_date=None):
    """Get timesheet summary for employee"""
    filters = {"docstatus": 1}
    
    if employee:
        filters["employee"] = employee
    
    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    
    timesheets = frappe.get_all(
        "Timesheet",
        filters=filters,
        fields=["name", "posting_date", "total_hours", "total_amount"]
    )
    
    total_hours = sum(ts.total_hours for ts in timesheets)
    total_amount = sum(ts.total_amount for ts in timesheets)
    
    return {
        "timesheets": timesheets,
        "total_count": len(timesheets),
        "total_hours": total_hours,
        "total_amount": total_amount
    }


@frappe.whitelist()
def get_project_timesheet_summary(project):
    """Get timesheet summary for a project"""
    time_logs = frappe.get_all(
        "Timesheet Detail",
        filters={"project": project},
        fields=["parent", "hours", "amount"]
    )
    
    total_hours = sum(tl.hours for tl in time_logs)
    total_amount = sum(tl.amount for tl in time_logs)
    
    return {
        "total_hours": total_hours,
        "total_amount": total_amount,
        "timesheet_count": len(set(tl.parent for tl in time_logs))
    }
