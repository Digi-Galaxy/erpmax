frappe.ui.form.on(Company, {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.chart_template) {
            frm.add_custom_button(__(Create Chart of Accounts), function() {
                frappe.call({
                    method: create_chart_of_accounts,
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__(Created {0} accounts, [r.message.length]));
                            frm.refresh();
                        }
                    }
                });
            }, __(Actions));
        }
    }
});
