import frappe
from frappe import _
from frappe.utils import now_datetime


CONTRACT_FLOWS = {
    "Service Contract": {
        "stages": ["Draft", "Pending Approval", "Active", "Completed", "Cancelled"],
        "transitions": {
            "Draft": ["Pending Approval", "Cancelled"],
            "Pending Approval": ["Active", "Draft"],
            "Active": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": ["Draft"],
        },
    },
    "Rental Contract": {
        "stages": ["Draft", "Pending Approval", "Active", "Completed", "Cancelled"],
        "transitions": {
            "Draft": ["Pending Approval", "Cancelled"],
            "Pending Approval": ["Active", "Draft"],
            "Active": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": ["Draft"],
        },
    },
    "Employee Contract": {
        "stages": ["Draft", "Pending Approval", "Active", "Completed", "Cancelled"],
        "transitions": {
            "Draft": ["Pending Approval", "Cancelled"],
            "Pending Approval": ["Active", "Draft"],
            "Active": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": ["Draft"],
        },
    },
    "Maintenance Schedule": {
        "stages": ["Draft", "Scheduled", "In Progress", "Completed", "Cancelled"],
        "transitions": {
            "Draft": ["Scheduled", "Cancelled"],
            "Scheduled": ["In Progress", "Cancelled"],
            "In Progress": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": ["Draft"],
        },
    },
    "Maintenance Visit": {
        "stages": ["Draft", "Scheduled", "In Progress", "Completed", "Cancelled"],
        "transitions": {
            "Draft": ["Scheduled", "Cancelled"],
            "Scheduled": ["In Progress", "Cancelled"],
            "In Progress": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": ["Draft"],
        },
    },
}


def get_flow_config(doctype):
    return CONTRACT_FLOWS.get(doctype, {})


def get_allowed_stages(doctype, current_stage):
    config = get_flow_config(doctype)
    transitions = config.get("transitions", {})
    return transitions.get(current_stage, [])


def validate_transition(doc, to_stage):
    config = get_flow_config(doc.doctype)
    transitions = config.get("transitions", {})
    allowed = transitions.get(doc.current_stage, [])

    if not allowed:
        frappe.throw(
            _("No further transitions allowed from stage '{0}'").format(doc.current_stage)
        )
    if to_stage not in allowed:
        frappe.throw(
            _("Cannot move from '{0}' to '{1}'. Allowed: {2}").format(
                doc.current_stage, to_stage, ", ".join(allowed)
            )
        )


def set_stage(doc, to_stage, action=None, notes=None):
    validate_transition(doc, to_stage)

    previous_stage = doc.current_stage
    doc.current_stage = to_stage
    doc.stage_updated = now_datetime()

    log = doc.append("stage_log", {})
    log.stage = to_stage
    log.timestamp = now_datetime()
    log.user = frappe.session.user
    log.action = action or f"Moved from {previous_stage} to {to_stage}"
    log.notes = notes

    doc.db_update()
    return True


@frappe.whitelist()
def set_document_stage(doctype, docname, to_stage, notes=None):
    doc = frappe.get_doc(doctype, docname)
    set_stage(doc, to_stage, notes=notes)
    return {"status": "success", "current_stage": doc.current_stage}
