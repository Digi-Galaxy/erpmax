frappe.ui.form.on("Transaction Deletion Record", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === "Running") {
            frm.add_custom_button(__("Refresh Status"), () => {
                frm.reload_doc();
            });
        }
    },
});
