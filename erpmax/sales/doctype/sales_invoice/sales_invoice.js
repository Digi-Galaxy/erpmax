frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        frm.add_custom_button(__("Email PDF"), () => open_email_dialog(frm), __("Send"));
        frm.add_custom_button(__("WhatsApp Print"), () => open_whatsapp_dialog(frm), __("Send"));
    },
});

async function get_send_defaults(frm) {
    return frappe.xcall("erpmax.sales.doctype.sales_invoice.sales_invoice.get_sales_invoice_send_defaults", {
        name: frm.doc.name,
    });
}

async function check_duplicate(frm, channel, recipient, print_format) {
    const result = await frappe.xcall("erpmax.sales.doctype.sales_invoice.sales_invoice.get_sales_invoice_send_warning", {
        name: frm.doc.name,
        channel,
        recipient,
        print_format,
    });

    if (!result.warning) {
        return false;
    }

    return await new Promise((resolve) => {
        frappe.confirm(result.warning, () => resolve(true), () => resolve(null));
    });
}

async function open_email_dialog(frm) {
    const defaults = await get_send_defaults(frm);

    const dialog = new frappe.ui.Dialog({
        title: __("Send Sales Invoice PDF"),
        fields: [
            {
                fieldname: "recipients",
                fieldtype: "Data",
                label: __("Recipients"),
                reqd: 1,
                default: defaults.customer_email || "",
                description: __("Comma separated email addresses"),
            },
            {
                fieldname: "print_format",
                fieldtype: "Link",
                label: __("Print Format"),
                options: "Print Format",
                default: defaults.print_format || frm.doc.print_format_override || "Standard",
            },
        ],
        primary_action_label: __("Send"),
        primary_action: async (values) => {
            const force = await check_duplicate(frm, "email", values.recipients, values.print_format);
            if (force === null) {
                return;
            }

            await frappe.xcall("erpmax.sales.doctype.sales_invoice.sales_invoice.send_sales_invoice_email", {
                name: frm.doc.name,
                recipients: values.recipients,
                print_format: values.print_format,
                force: force ? 1 : 0,
            });

            dialog.hide();
            frappe.show_alert({ message: __("Invoice email sent"), indicator: "green" });
            frm.reload_doc();
        },
    });

    dialog.show();
}

async function open_whatsapp_dialog(frm) {
    const defaults = await get_send_defaults(frm);

    const dialog = new frappe.ui.Dialog({
        title: __("Send Sales Invoice via WhatsApp"),
        fields: [
            {
                fieldname: "mobile_no",
                fieldtype: "Data",
                label: __("WhatsApp Number"),
                reqd: 1,
                default: defaults.customer_mobile || "",
            },
            {
                fieldname: "print_format",
                fieldtype: "Link",
                label: __("Print Format"),
                options: "Print Format",
                default: defaults.print_format || frm.doc.print_format_override || "Standard",
            },
        ],
        primary_action_label: __("Open WhatsApp"),
        primary_action: async (values) => {
            const force = await check_duplicate(frm, "whatsapp", values.mobile_no, values.print_format);
            if (force === null) {
                return;
            }

            const result = await frappe.xcall("erpmax.sales.doctype.sales_invoice.sales_invoice.prepare_sales_invoice_whatsapp", {
                name: frm.doc.name,
                mobile_no: values.mobile_no,
                print_format: values.print_format,
                force: force ? 1 : 0,
            });

            dialog.hide();
            window.open(result.whatsapp_url, "_blank", "noopener,noreferrer");
            frappe.show_alert({ message: __("WhatsApp share opened"), indicator: "green" });
            frm.reload_doc();
        },
    });

    dialog.show();
}
