frappe.ui.form.on("Settlement", {
    setup: function(frm) {
        frm.set_query("sales_invoice", "customer_allocations", function() {
            return {
                filters: {
                    customer: frm.doc.customer,
                    company: frm.doc.company,
                    docstatus: 1,
                    outstanding_amount: [">", 0]
                }
            };
        });
        frm.set_query("purchase_invoice", "supplier_allocations", function() {
            return {
                filters: {
                    supplier: frm.doc.supplier,
                    company: frm.doc.company,
                    docstatus: 1,
                    outstanding_amount: [">", 0]
                }
            };
        });
    },
    customer: function(frm) {
        frm.clear_table("customer_allocations");
        frm.refresh_field("customer_allocations");
        if (frm.doc.customer && frm.doc.company) {
            frappe.call({
                method: "erpmax.accounting.api.settlement.get_party_account",
                args: {party_type: "Customer", party: frm.doc.customer, company: frm.doc.company},
                callback: function(r) {
                    if (r.message) frm.set_value("customer_receivable_account", r.message);
                }
            });
        }
    },
    supplier: function(frm) {
        frm.clear_table("supplier_allocations");
        frm.refresh_field("supplier_allocations");
        if (frm.doc.supplier && frm.doc.company) {
            frappe.call({
                method: "erpmax.accounting.api.settlement.get_party_account",
                args: {party_type: "Supplier", party: frm.doc.supplier, company: frm.doc.company},
                callback: function(r) {
                    if (r.message) frm.set_value("supplier_payable_account", r.message);
                }
            });
        }
    },
    refresh: function(frm) {
        frm.trigger("update_totals");
    }
});

frappe.ui.form.on("Settlement Customer Allocation", {
    allocate_amount: function(frm, cdt, cdn) {
        frm.trigger("update_totals");
    },
    sales_invoice: function(frm) {
        frm.trigger("update_totals");
    }
});

frappe.ui.form.on("Settlement Supplier Allocation", {
    allocate_amount: function(frm, cdt, cdn) {
        frm.trigger("update_totals");
    },
    purchase_invoice: function(frm) {
        frm.trigger("update_totals");
    }
});
