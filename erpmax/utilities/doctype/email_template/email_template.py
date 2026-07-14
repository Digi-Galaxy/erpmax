# Copyright (c) 2024, ERPMax and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
import re


class EmailTemplate(Document):
    def validate(self):
        self.validate_template()
        self.validate_variables()
    
    def validate_template(self):
        """Validate email template"""
        if not self.message:
            frappe.throw(_("Message is required"))
    
    def validate_variables(self):
        """Validate that all required variables are defined"""
        if not self.variables:
            return
        
        # Extract variables from message
        message_variables = set(re.findall(r'\{\{(\w+)\}\}', self.message or ""))
        
        # Get defined variables
        defined_variables = set(v.variable_name for v in self.variables)
        
        # Check for undefined variables
        undefined = message_variables - defined_variables
        if undefined:
            frappe.msgprint(_("Warning: Variables used in message but not defined: {0}").format(
                ", ".join(undefined)
            ))
        
        # Check for unused variables
        unused = defined_variables - message_variables
        if unused:
            frappe.msgprint(_("Warning: Variables defined but not used in message: {0}").format(
                ", ".join(unused)
            ))
    
    def render(self, data):
        """
        Render template with data.
        
        Args:
            data: Dictionary of variable values
        
        Returns:
            tuple: (subject, message) with variables replaced
        """
        subject = self.subject
        message = self.message
        
        # Replace variables
        for key, value in data.items():
            placeholder = "{{" + key + "}}"
            subject = subject.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        return subject, message


def get_email_template(template_name, data):
    """
    Get and render email template.
    
    Args:
        template_name: Name of the template
        data: Dictionary of variable values
    
    Returns:
        tuple: (subject, message)
    """
    template = frappe.get_doc("Email Template", template_name)
    return template.render(data)


def get_available_templates(module=None):
    """Get list of available email templates"""
    filters = {"enabled": 1}
    if module:
        filters["module"] = module
    
    return frappe.get_all(
        "Email Template",
        filters=filters,
        fields=["name", "template_name", "subject", "module"]
    )


@frappe.whitelist()
def send_email_from_template(template_name, recipients, data, sender=None):
    """
    Send email using template.
    
    Args:
        template_name: Name of the template
        recipients: List of email recipients
        data: Dictionary of variable values
        sender: Optional sender email
    """
    subject, message = get_email_template(template_name, data)
    
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        sender=sender
    )
    
    frappe.msgprint(_("Email sent successfully"))
