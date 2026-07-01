import json
import re
from urllib.parse import quote

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, get_url, getdate, nowdate

SEND_LOG_PREFIX = "ERPMax Send Log::"


def get_next_recurrence_date(from_date, frequency, interval):
    if not from_date or not frequency:
        return None

    interval = interval or 1
    from_date = getdate(from_date)

    if frequency == "Daily":
        return add_days(from_date, interval)
    if frequency == "Weekly":
        return add_days(from_date, 7 * interval)
    if frequency == "Monthly":
        return add_months(from_date, interval)
    if frequency == "Quarterly":
        return add_months(from_date, 3 * interval)
    if frequency == "Yearly":
        return add_months(from_date, 12 * interval)

    return None


def get_customer_defaults(customer):
    if not customer:
        return {}

    return frappe.db.get_value(
        "Customer",
        customer,
        [
            "customer_name",
            "payment_method",
            "email",
            "mobile",
            "phone",
            "default_sales_invoice_print_format",
            "default_print_heading",
            "print_language",
            "invoice_table_format",
            "invoice_wording",
            "terms_and_conditions_text",
            "use_custom_letter_head",
            "letter_head",
            "apply_retention_by_default",
            "default_retention_percentage",
            "default_retention_account",
        ],
        as_dict=True,
    ) or {}


def get_company_print_defaults(company):
    if not company or not frappe.db.exists("PDF Settings", company):
        return {}

    return frappe.db.get_value(
        "PDF Settings",
        company,
        [
            "allow_customer_print_overrides",
            "default_sales_invoice_print_format",
            "default_print_heading",
            "default_invoice_table_format",
            "default_invoice_wording",
            "default_terms_and_conditions",
        ],
        as_dict=True,
    ) or {}


def resolve_print_format(doc, print_format=None):
    return print_format or doc.print_format_override or "Standard"


def split_recipients(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [v.strip() for v in value if v and str(v).strip()]
    parts = re.split(r"[,;\n]", str(value))
    return [p.strip() for p in parts if p.strip()]


def normalize_whatsapp_number(number):
    if not number:
        return ""
    number = str(number).strip()
    if number.startswith("+"):
        number = number[1:]
    return re.sub(r"\D", "", number)


def get_send_log_payload(content):
    if not content or SEND_LOG_PREFIX not in content:
        return None
    try:
        payload = content.split(SEND_LOG_PREFIX, 1)[1].strip()
        return json.loads(payload)
    except Exception:
        return None


def log_send_event(doc, channel, recipient, print_format, event, extra=None):
    payload = {
        "channel": channel,
        "recipient": recipient,
        "print_format": print_format,
        "event": event,
        "user": frappe.session.user,
        "timestamp": str(frappe.utils.now_datetime()),
    }
    if extra:
        payload.update(extra)

    readable = (
        f"{channel.title()} {event.replace('_', ' ')} for {recipient or 'unknown recipient'} "
        f"using print format {print_format}."
    )
    doc.add_comment("Info", f"{readable} {SEND_LOG_PREFIX} {json.dumps(payload, ensure_ascii=True)}")
    return payload


def get_last_send_event(docname, channel, recipient, print_format):
    comments = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": "Sales Invoice",
            "reference_name": docname,
            "comment_type": "Info",
        },
        fields=["name", "content", "creation", "owner"],
        order_by="creation desc",
        limit=30,
    )

    for comment in comments:
        payload = get_send_log_payload(comment.content)
        if not payload:
            continue
        if payload.get("channel") != channel:
            continue
        if (payload.get("recipient") or "") != (recipient or ""):
            continue
        if (payload.get("print_format") or "") != (print_format or ""):
            continue
        payload["creation"] = comment.creation
        payload["owner"] = comment.owner
        return payload

    return None


def get_duplicate_send_message(docname, channel, recipient, print_format):
    last_event = get_last_send_event(docname, channel, recipient, print_format)
    if not last_event:
        return None

    return _(
        "This invoice was already sent by {0} to {1} using {2} on {3}. Confirm if you want to resend."
    ).format(
        channel.title(),
        recipient,
        print_format,
        last_event.get("creation"),
    )


def build_print_url(doc, print_format=None):
    print_format = resolve_print_format(doc, print_format)
    params = [
        ("doctype", "Sales Invoice"),
        ("name", doc.name),
        ("format", print_format),
    ]
    if doc.no_letterhead:
        params.append(("no_letterhead", 1))
    if doc.print_language:
        params.append(("_lang", doc.print_language))

    query = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params)
    return f"{get_url()}/printview?{query}"


class SalesInvoice(Document):
    def validate(self):
        if self.is_recurring_invoice and not self.recurrence_frequency:
            frappe.throw(_("Recurrence Frequency is required for recurring invoices."))

        if self.recurrence_end_date and self.next_invoice_date and getdate(self.next_invoice_date) > getdate(self.recurrence_end_date):
            frappe.throw(_("Next Invoice Date cannot be after Recurrence End Date."))

    def before_save(self):
        self.apply_customer_print_defaults()
        self.update_retention_defaults()
        self.update_recurring_defaults()

        if self.customer:
            settings = frappe.get_single("ERPMax Settings")
            if settings.show_previous_balance:
                self.set_previous_balance()

    def onload(self):
        if self.customer and self.get("__islocal"):
            settings = frappe.get_single("ERPMax Settings")
            if settings.show_previous_balance:
                self.set_previous_balance()

    def apply_customer_print_defaults(self):
        customer_defaults = get_customer_defaults(self.customer)
        company_defaults = get_company_print_defaults(self.company)
        allow_customer_overrides = company_defaults.get("allow_customer_print_overrides") if company_defaults else 0

        self.customer_name = self.customer_name or customer_defaults.get("customer_name")
        self.payment_method = self.payment_method or customer_defaults.get("payment_method")

        if not self.print_format_override:
            self.print_format_override = (
                customer_defaults.get("default_sales_invoice_print_format") if allow_customer_overrides else None
            ) or company_defaults.get("default_sales_invoice_print_format")

        if not self.print_heading:
            self.print_heading = (
                customer_defaults.get("default_print_heading") if allow_customer_overrides else None
            ) or company_defaults.get("default_print_heading")

        if not self.print_language:
            self.print_language = customer_defaults.get("print_language")

        if not self.invoice_table_format:
            self.invoice_table_format = (
                customer_defaults.get("invoice_table_format") if allow_customer_overrides else None
            ) or company_defaults.get("default_invoice_table_format")

        if not self.invoice_wording:
            self.invoice_wording = (
                customer_defaults.get("invoice_wording") if allow_customer_overrides else None
            ) or company_defaults.get("default_invoice_wording")

        if not self.terms_and_conditions_text:
            self.terms_and_conditions_text = (
                customer_defaults.get("terms_and_conditions_text") if allow_customer_overrides else None
            ) or company_defaults.get("default_terms_and_conditions")

        if not self.letter_head and allow_customer_overrides and customer_defaults.get("use_custom_letter_head"):
            self.letter_head = customer_defaults.get("letter_head")

    def update_retention_defaults(self):
        customer_defaults = get_customer_defaults(self.customer)
        if customer_defaults.get("apply_retention_by_default") and not self.apply_retention:
            self.apply_retention = 1

        if self.apply_retention:
            if not self.retention_percentage:
                self.retention_percentage = customer_defaults.get("default_retention_percentage") or 0
            if not self.retention_account:
                self.retention_account = customer_defaults.get("default_retention_account")

    def update_recurring_defaults(self):
        if not self.is_recurring_invoice:
            return

        self.recurrence_interval = self.recurrence_interval or 1
        self.recurrence_start_date = self.recurrence_start_date or self.posting_date

        if not self.next_invoice_date:
            self.next_invoice_date = get_next_recurrence_date(
                self.recurrence_start_date,
                self.recurrence_frequency,
                self.recurrence_interval,
            )

    def set_previous_balance(self):
        balance = frappe.db.sql(
            """
            SELECT COALESCE(SUM(outstanding_amount), 0)
            FROM `tabSales Invoice`
            WHERE customer = %s
                AND docstatus = 1
                AND name != %s
                AND outstanding_amount > 0
        """,
            (self.customer, self.name or ""),
        )

        self.previous_balance = balance[0][0] if balance else 0

    def on_submit(self):
        pass

    def on_cancel(self):
        pass


@frappe.whitelist()
def get_sales_invoice_send_defaults(name):
    doc = frappe.get_doc("Sales Invoice", name)
    customer_defaults = get_customer_defaults(doc.customer)
    return {
        "customer_email": customer_defaults.get("email") or "",
        "customer_mobile": customer_defaults.get("mobile") or customer_defaults.get("phone") or "",
        "print_format": resolve_print_format(doc),
        "print_language": doc.print_language or "",
    }


@frappe.whitelist()
def get_sales_invoice_send_warning(name, channel, recipient=None, print_format=None):
    doc = frappe.get_doc("Sales Invoice", name)
    chosen_format = resolve_print_format(doc, print_format)
    recipient = recipient or ""
    return {
        "warning": get_duplicate_send_message(doc.name, channel, recipient, chosen_format),
        "print_format": chosen_format,
    }


@frappe.whitelist()
def send_sales_invoice_email(name, recipients=None, print_format=None, force=0):
    doc = frappe.get_doc("Sales Invoice", name)
    chosen_format = resolve_print_format(doc, print_format)
    recipient_list = split_recipients(recipients)
    if not recipient_list:
        defaults = get_customer_defaults(doc.customer)
        recipient_list = split_recipients(defaults.get("email"))

    if not recipient_list:
        frappe.throw(_("Recipient email is required."))

    recipient_key = ", ".join(recipient_list)
    warning = get_duplicate_send_message(doc.name, "email", recipient_key, chosen_format)
    if warning and not frappe.utils.cint(force):
        frappe.throw(warning)

    attachment = frappe.attach_print(
        "Sales Invoice",
        doc.name,
        print_format=chosen_format,
        lang=doc.print_language,
        print_letterhead=not frappe.utils.cint(doc.no_letterhead),
        letterhead=doc.letter_head,
    )

    message = doc.invoice_wording or _("Please find attached Sales Invoice {0}.").format(doc.name)
    frappe.sendmail(
        recipients=recipient_list,
        subject=_("Sales Invoice {0}").format(doc.name),
        message=message,
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        attachments=[attachment],
        delayed=False,
    )

    log_send_event(
        doc,
        "email",
        recipient_key,
        chosen_format,
        "pdf_sent",
        {"attachment": attachment.get("fname")},
    )

    return {"recipients": recipient_list, "print_format": chosen_format}


@frappe.whitelist()
def prepare_sales_invoice_whatsapp(name, mobile_no=None, print_format=None, force=0):
    doc = frappe.get_doc("Sales Invoice", name)
    chosen_format = resolve_print_format(doc, print_format)
    defaults = get_customer_defaults(doc.customer)
    recipient = mobile_no or defaults.get("mobile") or defaults.get("phone")
    normalized = normalize_whatsapp_number(recipient)
    if not normalized:
        frappe.throw(_("Customer mobile/WhatsApp number is required."))

    warning = get_duplicate_send_message(doc.name, "whatsapp", normalized, chosen_format)
    if warning and not frappe.utils.cint(force):
        frappe.throw(warning)

    print_url = build_print_url(doc, chosen_format)
    amount = doc.grand_total or doc.total or 0
    message = chr(10).join([
        _("Sales Invoice {0} for {1}").format(doc.name, doc.customer_name or doc.customer),
        _("Amount: {0}").format(amount),
        print_url,
    ])
    whatsapp_url = f"https://wa.me/{normalized}?text={quote(message)}"

    log_send_event(
        doc,
        "whatsapp",
        normalized,
        chosen_format,
        "share_opened",
        {"print_url": print_url},
    )

    return {
        "recipient": normalized,
        "print_format": chosen_format,
        "print_url": print_url,
        "whatsapp_url": whatsapp_url,
    }


@frappe.whitelist()
def create_next_recurring_sales_invoice(source_name, posting_date=None):
    source = frappe.get_doc("Sales Invoice", source_name)

    if not source.is_recurring_invoice:
        frappe.throw(_("This Sales Invoice is not marked as recurring."))

    target_date = getdate(posting_date or source.next_invoice_date or source.posting_date)
    end_date = getdate(source.recurrence_end_date) if source.recurrence_end_date else None
    if end_date and target_date > end_date:
        frappe.throw(_("Recurring period has ended for this Sales Invoice."))

    new_invoice = frappe.copy_doc(source)
    new_invoice.name = None
    new_invoice.amended_from = None
    new_invoice.docstatus = 0
    new_invoice.posting_date = target_date
    new_invoice.delivery_date = target_date
    if source.due_date:
        new_invoice.due_date = target_date
    new_invoice.is_recurring_invoice = 0
    new_invoice.generated_from_recurring = source.name
    new_invoice.last_generated_invoice = None
    new_invoice.last_generated_on = None
    new_invoice.next_invoice_date = None
    new_invoice.recurrence_end_date = None
    new_invoice.recurrence_start_date = None
    new_invoice.insert(ignore_permissions=True)

    source.last_generated_invoice = new_invoice.name
    source.last_generated_on = nowdate()
    source.next_invoice_date = get_next_recurrence_date(
        target_date,
        source.recurrence_frequency,
        source.recurrence_interval,
    )
    source.save(ignore_permissions=True)

    return new_invoice.name
