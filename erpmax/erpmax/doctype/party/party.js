frappe.ui.form.on("Party", {
    refresh: function(frm) {
        if (!frappe.boot.erpmax_toggles) {
            frappe.call({
                method: "erpmax.utils.feature_toggle.get_feature_toggles",
                callback: function(r) {
                    frappe.boot.erpmax_toggles = r.message || {};
                    apply_party_toggles(frm);
                }
            });
        } else {
            apply_party_toggles(frm);
        }
    }
});

function apply_party_toggles(frm) {
    var t = frappe.boot.erpmax_toggles || {};
    frm.toggle_display("sb_tax_compliance", t.fea_cnic || t.fea_ntn || t.fea_strn);
    frm.toggle_display("cnic_number", t.fea_cnic);
    frm.toggle_display("ntn_number", t.fea_ntn);
    frm.toggle_display("column_break_tax", t.fea_cnic || t.fea_ntn || t.fea_strn);
    frm.toggle_display("strn_number", t.fea_strn);
}
