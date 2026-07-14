(function () {
    if (window.__erpmax_geo_bootstrap_loaded) return;
    window.__erpmax_geo_bootstrap_loaded = true;

    var GEO_FIELDS_URL = "/assets/erpmax/js/geo_fields.js?v=20260714_3";

    function patch_runtime() {
        var Geo = window.erpmax_geo || (window.erpmax_geo = {});
        if (!Geo.settings) Geo.settings = {};
        if (!Geo.field_map) Geo.field_map = {};
        if (!Geo._config_promises) Geo._config_promises = {};
        if (!Geo._config_cache) Geo._config_cache = {};

        if (typeof Geo.load_config !== "function") {
            Geo.load_config = function (doctype) {
                var key = doctype || "__global__";
                if (Geo._config_cache[key]) return Promise.resolve(Geo._config_cache[key]);
                if (Geo._config_promises[key]) return Geo._config_promises[key];
                Geo._config_promises[key] = frappe.call({
                    method: "erpmax.erpmax_geo.registry.get_geo_config",
                    args: { doctype: doctype || "" },
                }).then(function (r) {
                    var cfg = r.message || {};
                    Geo.settings = cfg;
                    Geo.field_map = cfg.field_map || {};
                    Geo._config_cache[key] = cfg;
                    return cfg;
                }).catch(function () {
                    var cfg = { field_map: {} };
                    Geo.settings = cfg;
                    Geo.field_map = {};
                    Geo._config_cache[key] = cfg;
                    return cfg;
                });
                return Geo._config_promises[key];
            };
        }

        if (window.frappe && frappe.ui && frappe.ui.form && frappe.ui.form.Form && !frappe.ui.form.Form.prototype.__erpmax_geo_refresh_patched) {
            var original_refresh = frappe.ui.form.Form.prototype.refresh;
            frappe.ui.form.Form.prototype.refresh = function () {
                var result = original_refresh ? original_refresh.apply(this, arguments) : undefined;
                var frm = this;
                Geo.load_config(frm.doctype).then(function () {
                    if (Geo.init_form) {
                        try {
                            Geo.init_form(frm);
                        } catch (error) {
                            console.warn("ERPMax geo init failed", error);
                        }
                    }
                });
                return result;
            };
            frappe.ui.form.Form.prototype.__erpmax_geo_refresh_patched = true;
        }
    }

    function ensure_geo_loaded() {
        patch_runtime();
        if (window.erpmax_geo && typeof window.erpmax_geo.load_config === "function") return;
        frappe.require(GEO_FIELDS_URL, function () {
            patch_runtime();
            if (window.erpmax_geo && window.cur_frm) {
                try {
                    window.erpmax_geo.init_form(window.cur_frm);
                } catch (error) {
                    console.warn("ERPMax geo bootstrap init failed", error);
                }
            }
        }, function () {
            console.warn("ERPMax geo bootstrap failed to load", GEO_FIELDS_URL);
        });
    }

    if (window.frappe && frappe.after_ajax) {
        frappe.after_ajax(ensure_geo_loaded);
    }
    setTimeout(ensure_geo_loaded, 0);
})();
