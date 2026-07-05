import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class ZatcaCsid(Document):
    pass


def _get_notification_recipients(company):
    recipients = set()

    linked_user = frappe.db.get_value("Company", company, "linked_user")
    if linked_user:
        recipients.add(linked_user)

    company_users = frappe.get_all(
        "Company User",
        filters={
            "company": company,
            "is_active": 1,
            "role": ["in", ["Company Admin", "Accounts Manager"]],
        },
        pluck="user_email",
    )
    recipients.update(user for user in company_users if user)

    if recipients:
        return sorted(recipients)

    fallback_users = frappe.get_all(
        "Has Role",
        filters={
            "role": ["in", ["System Manager", "Accounts Manager"]],
            "parenttype": "User",
        },
        pluck="parent",
    )
    recipients.update(user for user in fallback_users if user)
    return sorted(recipients)


def _notification_exists_today(user, docname):
    return frappe.db.exists(
        "Notification Log",
        {
            "for_user": user,
            "document_type": "Zatca Csid",
            "document_name": docname,
            "type": "Alert",
            "creation": [">=", f"{nowdate()} 00:00:00"],
        },
    )


def _send_renewal_notifications(renewal_due):
    notified = []

    for row in renewal_due:
        recipients = [
            user
            for user in _get_notification_recipients(row["company"])
            if not _notification_exists_today(user, row["name"])
        ]
        if not recipients:
            continue

        subject = "ZATCA CSID renewal due in {days_left} day(s) for {company}".format(
            days_left=row["days_left"],
            company=row["company"],
        )
        email_content = (
            "CSID <b>{name}</b> for company <b>{company}</b> ".format(
                name=row["name"],
                company=row["company"],
            )
            + "expires in <b>{days_left}</b> day(s).".format(days_left=row["days_left"])
        )

        enqueue_create_notification(
            recipients,
            {
                "type": "Alert",
                "subject": subject,
                "email_content": email_content,
                "document_type": "Zatca Csid",
                "document_name": row["name"],
                "from_user": "Administrator",
            },
        )
        notified.append({"name": row["name"], "recipients": recipients})

    return notified


@frappe.whitelist()
def renew_csid_if_needed():
    today = getdate(nowdate())
    renewal_window_days = 30
    records = frappe.get_all(
        "Zatca Csid",
        fields=["name", "company", "csid_type", "expiry_date", "status"],
        filters={"expiry_date": ["is", "set"]},
        order_by="expiry_date asc",
    )

    expired = []
    renewal_due = []

    for row in records:
        expiry_date = getdate(row.expiry_date)
        days_left = (expiry_date - today).days

        if days_left < 0:
            if row.status != "Expired":
                frappe.db.set_value("Zatca Csid", row.name, "status", "Expired")
            expired.append({
                "name": row.name,
                "company": row.company,
                "csid_type": row.csid_type,
                "days_overdue": abs(days_left),
            })
            continue

        if days_left <= renewal_window_days:
            renewal_due.append({
                "name": row.name,
                "company": row.company,
                "csid_type": row.csid_type,
                "days_left": days_left,
            })

    notified = _send_renewal_notifications(renewal_due)

    return {
        "checked": len(records),
        "expired": expired,
        "renewal_due": renewal_due,
        "notified": notified,
        "renewal_window_days": renewal_window_days,
    }
