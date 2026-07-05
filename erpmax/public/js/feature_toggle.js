frappe.provide("erpmax.feature");

erpmax.feature.get_toggles = function(callback) {
    if (erpmax.feature._toggles) {
        if (callback) callback(erpmax.feature._toggles);
        return;
    }
    frappe.call({
        method: "erpmax.erpmax.utils.feature_toggle.get_feature_toggles",
        callback: function(r) {
            erpmax.feature._toggles = r.message || {};
            if (callback) callback(erpmax.feature._toggles);
        }
    });
};

erpmax.feature.is_enabled = function(feature_key, callback) {
    erpmax.feature.get_toggles(function(toggles) {
        if (callback) callback(!!toggles["fea_" + feature_key]);
    });
};
