(function () {
    const Geo = {};
    Geo.settings = {};
    Geo.field_map = {};
    Geo._config_promises = {};
    Geo._config_cache = {};

    function find_field_name(frm, fieldname) {
        if (!frm || !frm.fields_dict) return null;
        const mapped = Geo.field_map && Geo.field_map[fieldname];
        if (mapped && frm.fields_dict[mapped]) return mapped;
        if (frm.fields_dict[fieldname]) return fieldname;
        return null;
    }

    function field(frm, fieldname) {
        const name = find_field_name(frm, fieldname);
        return name ? frm.fields_dict[name] : null;
    }

    function has_field(frm, fieldname) {
        return !!find_field_name(frm, fieldname);
    }

    function get_value(frm, fieldname) {
        const name = find_field_name(frm, fieldname);
        return name ? (frm.doc[name] || "") : "";
    }

    function set_value(frm, fieldname, value) {
        const name = find_field_name(frm, fieldname);
        if (!name) return Promise.resolve();
        if ((frm.doc[name] || "") === (value || "")) return Promise.resolve();
        return frm.set_value(name, value);
    }

    function clear_value(frm, fieldname) {
        return set_value(frm, fieldname, "");
    }

    function set_label_if_present(frm, fieldname, label) {
        const name = find_field_name(frm, fieldname);
        if (name && label) frm.set_df_property(name, "label", label);
    }

    function set_visible_if_present(frm, fieldname, visible) {
        const name = find_field_name(frm, fieldname);
        if (name) frm.set_df_property(name, "hidden", visible ? 0 : 1);
    }

    function set_description_if_present(frm, fieldname, description) {
        const name = find_field_name(frm, fieldname);
        if (name) frm.set_df_property(name, "description", description || "");
    }

    function bind_input_once(frm, fieldname, event_name, handler) {
        const f = field(frm, fieldname);
        const name = find_field_name(frm, fieldname);
        if (!f || !name || !f.$wrapper) return;
        const namespace = ".erpmaxgeo_" + name;
        f.$wrapper.off(namespace);
        const events = (event_name || "input").split(/\s+/).filter(Boolean).map(function (ev) {
            return ev + namespace;
        }).join(" ");
        f.$wrapper.on(events, "input", handler);
    }

    function patch_form_refresh() {
        const Form = frappe && frappe.ui && frappe.ui.form && frappe.ui.form.Form;
        if (!Form || !Form.prototype || Form.prototype.__erpmax_geo_refresh_patched) return;
        const original_refresh = Form.prototype.refresh;
        Form.prototype.refresh = function () {
            const result = original_refresh ? original_refresh.apply(this, arguments) : undefined;
            try {
                Geo.init_form(this);
            } catch (error) {
                console.warn("ERPMax geo init failed", error);
            }
            return result;
        };
        Form.prototype.__erpmax_geo_refresh_patched = true;
    }

    let LEAFLET_LOADED = false;
    let MAP_INIT_CALLBACKS = [];

    function load_leaflet(cb) {
        if (window.L) { LEAFLET_LOADED = true; if (cb) cb(); return; }
        MAP_INIT_CALLBACKS.push(cb);
        if (LEAFLET_LOADED) return;
        LEAFLET_LOADED = true;
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
        document.head.appendChild(link);
        const script = document.createElement("script");
        script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
        script.onload = () => { MAP_INIT_CALLBACKS.forEach(function (fn) { if (fn) fn(); }); MAP_INIT_CALLBACKS = []; };
        script.onerror = () => { console.warn("Leaflet map failed to load"); };
        document.head.appendChild(script);
    }

    let MAP_CACHE = {};

    function get_map_key(frm) {
        if (!frm) return "";
        if (frm.doc && frm.doc.name) return frm.doctype + "::" + frm.doc.name;
        if (!frm.__erpmax_geo_map_key) {
            frm.__erpmax_geo_map_key = frm.doctype + "::" + frappe.utils.get_random(6);
        }
        return frm.__erpmax_geo_map_key;
    }

    function get_map(frm) {
        const idx = get_map_key(frm);
        if (MAP_CACHE[idx]) return MAP_CACHE[idx];
        return null;
    }

    function set_map(frm, map_obj) {
        const idx = get_map_key(frm);
        MAP_CACHE[idx] = map_obj;
    }

    function clamp_to_boundary(m, latlng) {
        if (!Geo.get_setting("clamp_marker_to_boundary", 1)) return latlng;
        if (!m || !m._circle || !latlng) return latlng;
        const center = m._circle.getLatLng();
        const radius = m._circle.getRadius();
        if (center.distanceTo(latlng) <= radius) return latlng;
        return m._last_valid || center;
    }

    Geo.get_setting = function (name, fallback) {
        return Geo.settings && Geo.settings[name] !== undefined ? Geo.settings[name] : fallback;
    };

    Geo.load_config = function (doctype) {
        const key = doctype || "__global__";
        if (Geo._config_cache[key]) return Promise.resolve(Geo._config_cache[key]);
        if (Geo._config_promises[key]) return Geo._config_promises[key];
        Geo._config_promises[key] = frappe.call({
            method: "erpmax.erpmax_geo.registry.get_geo_config",
            args: { doctype: doctype || "" },
        }).then(function (r) {
            const cfg = r.message || {};
            Geo.settings = cfg;
            Geo.field_map = cfg.field_map || {};
            Geo._config_cache[key] = cfg;
            return cfg;
        }).catch(function () {
            const cfg = { field_map: {} };
            Geo.settings = cfg;
            Geo.field_map = {};
            Geo._config_cache[key] = cfg;
            return cfg;
        });
        return Geo._config_promises[key];
    };

    function remove_map(frm) {
        const idx = get_map_key(frm);
        const m = MAP_CACHE[idx];
        if (m) {
            if (m._marker) m._map.removeLayer(m._marker);
            if (m._circle) m._map.removeLayer(m._circle);
            m._map.off();
            m._map.remove();
        }
        delete MAP_CACHE[idx];
    }

    function init_map(frm) {
        const actual_name = find_field_name(frm, "map_view");
        const field = actual_name ? frm.fields_dict[actual_name] : null;
        if (!field || !field.$wrapper) return;
        load_leaflet(function () {
            if (!window.L) return;
            const wrapper = field.$wrapper.get(0);
            if (!wrapper) return;
            wrapper.innerHTML = '<div id="map-' + (frm.doc.name || "new") + '" style="height:320px;border-radius:8px;border:1px solid #d1d8dd;"></div>';
            const container = wrapper.firstChild;
            const lat = parseFloat(get_value(frm, "latitude")) || 24.86;
            const lng = parseFloat(get_value(frm, "longitude")) || 67.01;
            const map = L.map(container, { zoomControl: true, attributionControl: false }).setView([lat, lng], 10);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(map);
            setTimeout(function () { map.invalidateSize(); }, 300);
            const marker = L.marker([lat, lng], { draggable: true }).addTo(map);
            let circle = null;
            let lastValid = L.latLng(lat, lng);

            marker.on("dragend", function () {
                const pos = clamp_to_boundary({ _circle: circle, _last_valid: lastValid }, marker.getLatLng());
                marker.setLatLng(pos);
                lastValid = pos;
                set_value(frm, "latitude", pos.lat.toFixed(6));
                set_value(frm, "longitude", pos.lng.toFixed(6));
                reverse_geocode_form(frm, pos.lat, pos.lng);
            });

            map.on("click", function (e) {
                const pos = clamp_to_boundary({ _circle: circle, _last_valid: lastValid }, e.latlng);
                marker.setLatLng(pos);
                lastValid = pos;
                set_value(frm, "latitude", pos.lat.toFixed(6));
                set_value(frm, "longitude", pos.lng.toFixed(6));
                reverse_geocode_form(frm, pos.lat, pos.lng);
            });

            set_map(frm, { _map: map, _marker: marker, _circle: circle, _last_valid: lastValid });
        });
    }

    function reverse_geocode_form(frm, lat, lng) {
        frappe.call({
            method: "erpmax.erpmax_geo.registry.reverse_geocode",
            args: { lat: lat, lon: lng },
            callback: function (r) {
                const data = r.message || {};
                if (!data.display_name) return;
                if (!get_value(frm, "address_line_1") && has_field(frm, "address_line_1")) {
                    const parts = [];
                    if (data.house_number) parts.push(data.house_number);
                    if (data.road) parts.push(data.road);
                    set_value(frm, "address_line_1", parts.join(", ") || data.display_name.split(",")[0].trim());
                }
                if (!get_value(frm, "city") && data.city && has_field(frm, "city")) set_value(frm, "city", data.city);
                if (!get_value(frm, "state") && data.state && has_field(frm, "state")) set_value(frm, "state", data.state);
                if (!get_value(frm, "zip_code") && data.postcode && has_field(frm, "zip_code")) set_value(frm, "zip_code", data.postcode);
                if (data.place_id) set_value(frm, "place_id", data.place_id);
                if (data.lat && data.lon) update_map_view(frm);
                Geo.sync_region(frm, false);
            },
        });
    }

    function update_map_view(frm) {
        const m = get_map(frm);
        if (!m) return;
        const lat = parseFloat(get_value(frm, "latitude"));
        const lng = parseFloat(get_value(frm, "longitude"));
        if (isNaN(lat) || isNaN(lng)) return;
        m._marker.setLatLng([lat, lng]);
        m._map.setView([lat, lng], m._map.getZoom());
    }

    function update_map_boundary(frm) {
        const m = get_map(frm);
        if (!m) return;
        frappe.call({
            method: "erpmax.erpmax_geo.registry.get_region_boundary",
            args: { country: get_value(frm, "country"), doc: frm.doc },
            callback: function (r) {
                const data = r.message || {};
                if (!data.lat) return;
                if (m._circle) m._map.removeLayer(m._circle);
                m._circle = L.circle([data.lat, data.lon], { radius: data.radius || 20000, color: "#2563eb", fillColor: "#3b82f6", fillOpacity: 0.1, weight: 2 }).addTo(m._map);
                if (!get_value(frm, "latitude") && !get_value(frm, "longitude")) {
                    m._marker.setLatLng([data.lat, data.lon]);
                    m._last_valid = L.latLng(data.lat, data.lon);
                }
                m._map.fitBounds(m._circle.getBounds().pad(0.2));
            },
        });
    }

    function get_country(frm) {
        return get_value(frm, "country");
    }

    function set_if_empty(frm, fieldname, value) {
        const name = find_field_name(frm, fieldname);
        if (!value || !name || frm.doc[name]) return;
        frm.set_value(name, value);
    }

    function set_label_if_present(frm, fieldname, label) {
        const name = find_field_name(frm, fieldname);
        if (label && name) frm.set_df_property(name, "label", label);
    }

    function set_visible_if_present(frm, fieldname, visible) {
        const name = find_field_name(frm, fieldname);
        if (name) frm.set_df_property(name, "hidden", visible ? 0 : 1);
    }

    function render_suggestions(input, rows, on_select) {
        hide_suggestions();
        if (!rows || !rows.length || !input) return;

        const rect = input.getBoundingClientRect();
        const box = document.createElement("div");
        box.id = "erpmax-geo-suggestions";
        box.style.cssText = [
            "position:fixed",
            "z-index:10000",
            "background:#fff",
            "border:1px solid #d1d8dd",
            "border-radius:6px",
            "box-shadow:0 8px 20px rgba(0,0,0,.12)",
            "max-height:220px",
            "overflow-y:auto",
            "font-size:12px",
            "width:" + rect.width + "px",
            "left:" + rect.left + "px",
            "top:" + (rect.bottom + 4) + "px",
        ].join(";");

        rows.forEach((row) => {
            const item = document.createElement("div");
            item.textContent = row.label || row.value;
            item.style.cssText = "padding:8px 10px;cursor:pointer;border-bottom:1px solid #f4f5f6";
            item.addEventListener("mouseenter", () => (item.style.background = "#f7f7f7"));
            item.addEventListener("mouseleave", () => (item.style.background = "#fff"));
            item.addEventListener("mousedown", (event) => {
                event.preventDefault();
                hide_suggestions();
                on_select(row);
            });
            box.appendChild(item);
        });
        document.body.appendChild(box);
    }

    function hide_suggestions() {
        const existing = document.getElementById("erpmax-geo-suggestions");
        if (existing) existing.remove();
    }

    function setup_autocomplete(frm, fieldname, method, get_args, on_select) {
        const actual_name = find_field_name(frm, fieldname);
        const field = actual_name ? frm.fields_dict[actual_name] : null;
        if (!field || !field.$wrapper) return;

        const namespace = ".erpmaxgeo_ac_" + actual_name;
        field.$wrapper.off(namespace);

        let timer = null;
        field.$wrapper.on("input" + namespace, "input", function () {
            clearTimeout(timer);
            const input = this;
            timer = setTimeout(() => {
                const args = get_args(input.value || "");
                if (!args.country) return hide_suggestions();
                frappe.call({
                    method,
                    args,
                    callback: (r) => render_suggestions(input, r.message || [], on_select),
                });
            }, 250);
        });
        field.$wrapper.on("focusout" + namespace, "input", () => setTimeout(hide_suggestions, 200));
    }

    function apply_country_context(frm) {
        const country = get_country(frm);
        if (!country) return;
        frappe.call({
                    method: "erpmax.erpmax_geo.registry.get_country_context",
            args: { country },
            callback(r) {
                const ctx = r.message || {};
                if (!ctx.country) return;
                set_if_empty(frm, "country_alpha_2", ctx.alpha_2);
                set_if_empty(frm, "country_language", ctx.language);
                set_if_empty(frm, "default_currency", ctx.currency);
                set_if_empty(frm, "timezone", ctx.timezone);
                set_if_empty(frm, "date_format", ctx.date_format);

                const fmt = ctx.id_format || {};
                if (frm.fields_dict.tax_id && fmt.business_label) {
                    frm.set_df_property("tax_id", "label", fmt.business_label);
                    frm.set_df_property("tax_id", "description", fmt.business_placeholder ? "Example: " + fmt.business_placeholder : "");
                }
                if (frm.fields_dict.registration_number && fmt.business_label) {
                    frm.set_df_property("registration_number", "description", fmt.business_placeholder ? "Example: " + fmt.business_placeholder : "");
                }

                apply_address_profile(frm, ctx.address_profile || {});
                Geo.sync_region(frm, false);
                Geo.update_map_boundary(frm);
            },
        });
    }

    function apply_address_profile(frm, profile) {
        const visible = new Set(profile.visible_fields || []);
        const always_visible = new Set(["country", "latitude", "longitude", "map_view", "address_line_1", "address_line_2", "place_id", "geofence_radius_m", "geofence_center_lat", "geofence_center_lng"]);
        const labels = profile.labels || {};

        [
            "state",
            "subdivision",
            "division",
            "district",
            "subdistrict",
            "union_council",
            "town",
            "city",
            "zip_code",
            "latitude",
            "longitude",
            "place_id",
            "map_view",
            "geofence_radius_m",
            "geofence_center_lat",
            "geofence_center_lng",
            "building_no",
            "street_name",
            "additional_no",
            "province",
            "address_line_1",
            "address_line_2",
        ].forEach((fieldname) => {
            set_visible_if_present(frm, fieldname, visible.has(fieldname) || always_visible.has(fieldname));
        });

        Object.keys(labels).forEach((fieldname) => set_label_if_present(frm, fieldname, labels[fieldname]));
        set_label_if_present(frm, "zip_code", labels.zip_code || "Postal Code / ZIP");
        set_label_if_present(frm, "state", labels.state || "State / Province / Region");

        const state_value = get_value(frm, "state");
        const city_value = get_value(frm, "city");
        set_description_if_present(frm, "division", state_value ? "Division under " + state_value : "Division under the selected state");
        set_description_if_present(frm, "district", city_value ? "District near " + city_value : (state_value ? "District under " + state_value : "District under the selected state"));
        set_description_if_present(frm, "subdistrict", city_value ? "Subdistrict / tehsil near " + city_value : "Subdistrict / tehsil under the selected district");
        set_description_if_present(frm, "town", city_value ? "Town / village near " + city_value : "Town / village under the selected district");

        if (profile.country === "Pakistan") {
            set_if_empty(frm, "state", get_value(frm, "state"));
        }
    }

    function refresh_region_hints(frm) {
        const country = get_country(frm);
        if (country !== "Pakistan") return;
        const state_value = get_value(frm, "state");
        const city_value = get_value(frm, "city");
        set_description_if_present(frm, "division", state_value ? "Division under " + state_value : "Division under the selected state");
        set_description_if_present(frm, "district", city_value ? "District near " + city_value : (state_value ? "District under " + state_value : "District under the selected state"));
        set_description_if_present(frm, "subdistrict", city_value ? "Subdistrict / tehsil near " + city_value : "Subdistrict / tehsil under the selected district");
        set_description_if_present(frm, "town", city_value ? "Town / village near " + city_value : "Town / village under the selected district");
    }

    function setup_geo_fields(frm) {
        setup_autocomplete(
            frm,
            "state",
            "erpmax.erpmax_geo.registry.search_states",
            (txt) => ({ country: get_country(frm), txt, limit: 20 }),
            (row) => {
                set_value(frm, "state", row.value);
                clear_value(frm, "city");
                Geo.sync_region(frm, false);
                refresh_region_hints(frm);
                Geo.update_map_boundary(frm);
            }
        );

        setup_autocomplete(
            frm,
            "city",
            "erpmax.erpmax_geo.registry.search_cities",
            (txt) => ({ country: get_country(frm), state: get_value(frm, "state") || "", txt, limit: 20 }),
            (row) => {
                set_value(frm, "city", row.value);
                if (!get_value(frm, "state") && row.state) set_value(frm, "state", row.state);
                Geo.sync_region(frm, false);
                refresh_region_hints(frm);
                Geo.update_map_boundary(frm);
            }
        );

        if (has_field(frm, "address_line_1")) {
            const place_field = field(frm, "address_line_1");
            if (place_field && place_field.$input && !place_field.__erpmax_place_autocomplete) {
                place_field.__erpmax_place_autocomplete = true;
                let timer = null;
                place_field.$input.on("input", function () {
                    clearTimeout(timer);
                    const q = (this.value || "").trim();
                    if (q.length < 3) return hide_suggestions();
                    timer = setTimeout(function () {
                        frappe.call({
                            method: "erpmax.erpmax_geo.registry.search_places",
                            args: {
                                query: q,
                                country: get_country(frm),
                                doc: frm.doc,
                                limit: 8,
                            },
                            callback: function (r) {
                                const results = r.message || [];
                                render_suggestions(place_field.$input.get(0), results, function (row) {
                                    const d = row.data || row;
                                    set_value(frm, "address_line_1", [d.house_number, d.road].filter(Boolean).join(", ") || (d.display_name || "").split(",")[0].trim());
                                    if (d.city) set_value(frm, "city", d.city);
                                    if (d.state) set_value(frm, "state", d.state);
                                    if (d.postcode) set_value(frm, "zip_code", d.postcode);
                                    if (d.place_id) set_value(frm, "place_id", d.place_id);
                                    if (d.lat && d.lon) {
                                        set_value(frm, "latitude", d.lat);
                                        set_value(frm, "longitude", d.lon);
                                        update_map_view(frm);
                                    }
                                    Geo.sync_region(frm, false);
                                    refresh_region_hints(frm);
                                    Geo.update_map_boundary(frm);
                                });
                            },
                        });
                    }, 350);
                });
                place_field.$input.on("blur", function () { setTimeout(hide_suggestions, 200); });
            }
        }
    }

    function bind_geo_events(frm) {
        bind_input_once(frm, "country", "change input", function () {
            Geo.on_country_change(frm);
            refresh_region_hints(frm);
            Geo.update_map_boundary(frm);
        });
        bind_input_once(frm, "state", "change input", function () {
            Geo.on_state_change(frm);
            refresh_region_hints(frm);
        });
        ["division", "district", "subdistrict", "town", "city", "zip_code"].forEach(function (name) {
            bind_input_once(frm, name, "change input", function () {
                Geo.on_address_part_change(frm);
                refresh_region_hints(frm);
                Geo.update_map_boundary(frm);
            });
        });
        bind_input_once(frm, "latitude", "change input", function () {
            Geo.update_map_view(frm);
        });
        bind_input_once(frm, "longitude", "change input", function () {
            Geo.update_map_view(frm);
        });
    }

    function should_skip_form(frm) {
        return !frm || ["DocType", "DocField", "DocPerm", "DocType Action", "DocType Link", "DocType State"].includes(frm.doctype);
    }

    function render_field_list_html(fields) {
        if (!fields || !fields.length) return "<div class='text-muted'>No fields found for the selected DocType.</div>";
        const items = fields.map(function (f) {
            return "<li style='margin-bottom:6px'><code>" + frappe.utils.escape_html(f.fieldname) + "</code> <span class='text-muted'>" + frappe.utils.escape_html(f.label || "") + "</span> <span class='text-muted' style='font-size:11px'>[" + frappe.utils.escape_html(f.fieldtype || "Data") + "]</span></li>";
        }).join("");
        return "<div style='line-height:1.6'><div class='text-muted' style='margin-bottom:8px'>Fields available on selected DocType:</div><ul style='margin:0;padding-left:18px'>" + items + "</ul></div>";
    }

    function geo_preview_group_for_field(field) {
        const fieldname = (field && field.fieldname) || "";
        if (fieldname === "country" || fieldname === "country_alpha_2") return "Country";
        if (fieldname === "address_line_1" || fieldname === "address_line_2") return "Address";
        if (["latitude", "longitude", "place_id", "map_view", "geofence_radius_m", "geofence_center_lat", "geofence_center_lng"].includes(fieldname)) return "Geo coordinates";
        if (fieldname === "region") return "Region";
        if (["state", "division", "district", "subdistrict", "town", "city", "zip_code"].includes(fieldname)) return "Administrative Areas";
        return "Other";
    }

    function render_geo_field_item(field) {
        return "<div class='erpmax-geo-relevant-field'><code>" + frappe.utils.escape_html(field.fieldname) + "</code> <span class='text-muted'>" + frappe.utils.escape_html(field.label || "") + "</span> <span class='text-muted' style='font-size:11px'>" + frappe.utils.escape_html(field.fieldtype || "Data") + "</span></div>";
    }

    function render_relevant_fields_html(fields) {
        if (!fields || !fields.length) return "<div class='text-muted'>No relevant fields were found for the selected DocType.</div>";
        const groups = { "Country": [], "Address": [], "Administrative Areas": [], "Geo coordinates": [], "Region": [], "Other": [] };
        fields.forEach(function (field) {
            const group_name = geo_preview_group_for_field(field);
            if (!groups[group_name]) groups[group_name] = [];
            groups[group_name].push(field);
        });

        const order = ["Country", "Address", "Administrative Areas", "Geo coordinates", "Region", "Other"];
        const sections = order.map(function (group_name) {
            const group_fields = groups[group_name] || [];
            if (!group_fields.length) return "";
            return [
                "<div class='erpmax-geo-preview-section'>",
                "<div class='erpmax-geo-preview-section-title'>" + frappe.utils.escape_html(group_name) + "</div>",
                "<div class='erpmax-geo-preview-section-body'>" + group_fields.map(render_geo_field_item).join("") + "</div>",
                "</div>",
            ].join("");
        }).filter(Boolean).join("");

        return "<div class='erpmax-geo-preview'><div class='text-muted' style='margin-bottom:8px'>Relevant fields fetched from the selected DocType:</div>" + sections + "</div>";
    }

    function render_field_palette_html(fields, query, suggestions, active) {
        const normalized = (query || "").trim().toLowerCase();
        const suggestionMap = {};
        Object.keys(suggestions || {}).forEach(function (key) {
            const item = suggestions[key] || {};
            if (item && item.fieldname) suggestionMap[item.fieldname] = item;
        });
        const suggested = new Set(Object.keys(suggestionMap));
        const visible = (fields || []).filter(function (f) {
            if (!normalized) return true;
            const haystack = ((f.fieldname || "") + " " + (f.label || "") + " " + (f.fieldtype || "")).toLowerCase();
            return haystack.indexOf(normalized) !== -1;
        });

        visible.sort(function (a, b) {
            const as = suggested.has(a.fieldname) ? 1 : 0;
            const bs = suggested.has(b.fieldname) ? 1 : 0;
            if (as !== bs) return bs - as;
            return (a.label || a.fieldname || "").localeCompare(b.label || b.fieldname || "");
        });

        const suggestedItems = visible.filter(function (f) { return suggested.has(f.fieldname); });
        const otherItems = visible.filter(function (f) { return !suggested.has(f.fieldname); });

        function itemHtml(f) {
            const is_active = active && active.active_source === f.fieldname;
            const suggestion = suggestionMap[f.fieldname] || {};
            const badge = suggestion.confidence ? "<span class='erpmax-geo-field-chip-badge is-" + frappe.utils.escape_html(suggestion.confidence) + "'>" + frappe.utils.escape_html(suggestion.confidence) + "</span>" : "";
            return "<button type='button' class='erpmax-geo-field-chip" + (is_active ? " is-active" : "") + (suggested.has(f.fieldname) ? " is-suggested" : "") + "' data-fieldname='" + frappe.utils.escape_html(f.fieldname) + "'>" +
                "<span class='erpmax-geo-field-chip-main'><code>" + frappe.utils.escape_html(f.fieldname) + "</code>" +
                "<span class='erpmax-geo-field-chip-label'>" + frappe.utils.escape_html(f.label || f.fieldname) + "</span></span>" +
                "<span class='erpmax-geo-field-chip-meta'>" + badge + "<span class='erpmax-geo-field-chip-type'>" + frappe.utils.escape_html(f.fieldtype || "Data") + "</span></span>" +
            "</button>";
        }

        const header = [
            "<div class='erpmax-geo-palette-head'>",
            "<div>",
            "<div class='erpmax-geo-palette-title'>Field Palette</div>",
            "<div class='erpmax-geo-palette-subtitle'>Click a field to fill the selected mapping cell.</div>",
            "</div>",
            "<input type='search' class='erpmax-geo-palette-search form-control' placeholder='Search fields...' value='" + frappe.utils.escape_html(query || "") + "' />",
            "</div>",
        ].join("");

        const empty = "<div class='text-muted' style='padding:10px 0'>No matching fields.</div>";
        return [
            "<div class='erpmax-geo-palette'>",
            header,
            suggestedItems.length ? "<div class='erpmax-geo-palette-group'><div class='erpmax-geo-palette-group-title'>Suggested</div><div class='erpmax-geo-field-grid'>" + suggestedItems.map(itemHtml).join("") + "</div></div>" : "",
            "<div class='erpmax-geo-palette-group'><div class='erpmax-geo-palette-group-title'>All Fields</div><div class='erpmax-geo-field-grid'>" + (otherItems.length ? otherItems.map(itemHtml).join("") : empty) + "</div></div>",
            "</div>",
        ].join("");
    }

    function ensure_geo_settings_styles() {
        if (document.getElementById("erpmax-geo-settings-styles")) return;
        const style = document.createElement("style");
        style.id = "erpmax-geo-settings-styles";
        style.textContent = [
            "#erpmax-geo-settings-layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(320px,0.95fr);gap:16px;align-items:start}",
            "#erpmax-geo-settings-layout .erpmax-geo-settings-column{min-width:0}",
            ".erpmax-geo-palette{border:1px solid var(--border-color);border-radius:12px;background:var(--card-bg);padding:12px;box-shadow:0 1px 2px rgba(0,0,0,.03)}",
            ".erpmax-geo-palette-head{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:10px;align-items:center;margin-bottom:12px}",
            ".erpmax-geo-palette-title{font-weight:600;font-size:14px;line-height:1.2}",
            ".erpmax-geo-palette-subtitle{font-size:12px;color:var(--text-muted);margin-top:4px}",
            ".erpmax-geo-palette-group + .erpmax-geo-palette-group{margin-top:14px}",
            ".erpmax-geo-palette-group-title{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--text-muted);margin-bottom:8px}",
            ".erpmax-geo-field-grid{display:flex;flex-direction:column;gap:8px;max-height:540px;overflow:auto;padding-right:2px}",
            ".erpmax-geo-field-chip{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;text-align:left;width:100%;border:1px solid var(--border-color);border-radius:10px;background:var(--bg-color);padding:9px 10px;transition:all .15s ease}",
            ".erpmax-geo-field-chip:hover{border-color:var(--primary);box-shadow:0 4px 12px rgba(0,0,0,.05)}",
            ".erpmax-geo-field-chip.is-suggested{border-color:rgba(37,99,235,.35);background:rgba(37,99,235,.04)}",
            ".erpmax-geo-field-chip.is-active{outline:2px solid var(--primary);outline-offset:1px}",
            ".erpmax-geo-field-chip-main{display:flex;flex-direction:column;gap:2px;min-width:0}",
            ".erpmax-geo-field-chip-label{font-size:12px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
            ".erpmax-geo-field-chip-meta{display:flex;align-items:center;gap:6px;justify-content:flex-end;flex-wrap:wrap}",
            ".erpmax-geo-field-chip-type{font-size:11px;color:var(--text-muted);background:var(--surface-bg);padding:2px 6px;border-radius:999px;white-space:nowrap}",
            ".erpmax-geo-field-chip-badge{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;padding:2px 6px;border-radius:999px;background:#eef2ff;color:#1e3a8a}",
            ".erpmax-geo-field-chip-badge.is-strong{background:#dcfce7;color:#166534}",
            ".erpmax-geo-field-chip-badge.is-medium{background:#ffedd5;color:#9a3412}",
            ".erpmax-geo-field-chip-badge.is-weak{background:#f3f4f6;color:#374151}",
            ".erpmax-geo-field-chip-badge.is-manual{background:#fee2e2;color:#991b1b}",
            ".erpmax-geo-preview{display:flex;flex-direction:column;gap:10px}",
            ".erpmax-geo-preview-section{border:1px solid var(--border-color);border-radius:10px;padding:10px 12px;background:var(--card-bg)}",
            ".erpmax-geo-preview-section-title{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:var(--text-muted);margin-bottom:8px}",
            ".erpmax-geo-preview-section-body{display:flex;flex-direction:column;gap:6px}",
            ".erpmax-geo-palette-search{height:36px}",
            "@media (max-width: 992px){#erpmax-geo-settings-layout{grid-template-columns:1fr}.erpmax-geo-palette-head{grid-template-columns:1fr}}",
        ].join("\n");
        document.head.appendChild(style);
    }

    function get_geo_settings_field_wrapper(frm, fieldname) {
        const name = find_field_name(frm, fieldname);
        return name && frm.fields_dict[name] ? frm.fields_dict[name].$wrapper : null;
    }

    function is_geo_settings_form(frm) {
        return frm && (frm.doctype === "Geo Settings" || frm.doctype === "Geo");
    }

    function get_or_create_palette_container(frm) {
        const wrapper = get_geo_settings_field_wrapper(frm, "field_palette_html");
        if (wrapper) return wrapper;

        if (frm.__erpmax_geo_palette_container && frm.__erpmax_geo_palette_container.length) {
            return frm.__erpmax_geo_palette_container;
        }

        const mappings = get_geo_settings_field_wrapper(frm, "doctype_mappings");
        const preview = get_geo_settings_field_wrapper(frm, "doctype_fields_html");
        const anchor = preview && preview.length ? preview : mappings;
        if (!anchor || !anchor.length) return null;

        const container = $("<div class='erpmax-geo-fallback-palette'></div>");
        anchor.after(container);
        frm.__erpmax_geo_palette_container = container;
        return container;
    }

    function set_geo_settings_html(frm, fieldname, html) {
        const name = find_field_name(frm, fieldname);
        if (!name) return;
        frm.set_df_property(name, "options", html || "");
        frm.refresh_field(name);
    }

    function get_palette_state(frm) {
        if (!frm.__erpmax_geo_settings_state) {
            frm.__erpmax_geo_settings_state = { doctype: "", fields: [], suggestions: {}, query: "", active: null };
        }
        return frm.__erpmax_geo_settings_state;
    }

    function render_palette_for_settings(frm) {
        const state = get_palette_state(frm);
        if (state.active && state.active.cdt && state.active.cdn && state.active.fieldname) {
            const row = locals[state.active.cdt] && locals[state.active.cdt][state.active.cdn];
            state.active.active_source = row ? row[state.active.fieldname] : "";
        }
        const html = render_field_palette_html(state.fields, state.query, state.suggestions, state.active);
        const wrapper = get_or_create_palette_container(frm);
        if (wrapper) {
            wrapper.html(html);
        }
        bind_palette_events(frm);
    }

    function bind_palette_events(frm) {
        const wrapper = get_or_create_palette_container(frm);
        if (!wrapper || wrapper.data("erpmaxBound")) return;
        wrapper.data("erpmaxBound", true);
        wrapper.on("input", ".erpmax-geo-palette-search", function () {
            const state = get_palette_state(frm);
            state.query = this.value || "";
            render_palette_for_settings(frm);
        });
        wrapper.on("click", ".erpmax-geo-field-chip", function () {
            const state = get_palette_state(frm);
            const target = state.active;
            if (!target || !target.cdn || !target.fieldname) return;
            const row = locals[target.cdt] && locals[target.cdt][target.cdn];
            if (!row) return;
            const source = this.getAttribute("data-fieldname") || "";
            frappe.model.set_value(target.cdt, target.cdn, target.fieldname, source);
            row[target.fieldname] = source;
            state.active = target;
            render_palette_for_settings(frm);
            frm.refresh_field("doctype_mappings");
        });
    }

    function render_settings_layout(frm) {
        const mappings = get_geo_settings_field_wrapper(frm, "doctype_mappings");
        const preview = get_geo_settings_field_wrapper(frm, "doctype_fields_html");
        const palette = get_or_create_palette_container(frm);
        if (!mappings || !preview || !palette) return;
        ensure_geo_settings_styles();

        let layout = document.getElementById("erpmax-geo-settings-layout");
        if (!layout) {
            layout = document.createElement("div");
            layout.id = "erpmax-geo-settings-layout";
            layout.innerHTML = "<div class='erpmax-geo-settings-column erpmax-geo-settings-left'></div><div class='erpmax-geo-settings-column erpmax-geo-settings-right'></div>";
            mappings.before(layout);
        }

        const left = layout.querySelector(".erpmax-geo-settings-left");
        const right = layout.querySelector(".erpmax-geo-settings-right");
        if (left && mappings.length && mappings[0].parentNode !== left) left.appendChild(mappings[0]);
        if (right) {
            if (preview.length && preview[0].parentNode !== right) right.appendChild(preview[0]);
            if (palette.length && palette[0].parentNode !== right) right.appendChild(palette[0]);
        }
    }

    function apply_row_field_options(frm, row, fields) {
        const grid = frm.fields_dict.doctype_mappings && frm.fields_dict.doctype_mappings.grid;
        const grid_row = grid && grid.grid_rows_by_docname ? grid.grid_rows_by_docname[row.name] : null;
        if (!grid_row || !fields || !fields.length) return;
        const options = [""]
            .concat(fields.map(function (f) { return f.fieldname; }))
            .join("\n");

        [
            "country_field",
            "state_field",
            "division_field",
            "district_field",
            "subdistrict_field",
            "town_field",
            "city_field",
            "zip_code_field",
            "address_line_1_field",
            "address_line_2_field",
            "latitude_field",
            "longitude_field",
            "place_id_field",
            "map_view_field",
            "region_field",
            "geofence_radius_field",
            "geofence_center_lat_field",
            "geofence_center_lng_field",
        ].forEach(function (fieldname) {
            const field = grid_row.fields_dict && grid_row.fields_dict[fieldname];
            if (!field) return;
            field.df.options = options;
            if (field.refresh_input) field.refresh_input();
        });

        bind_mapping_row_events(frm, row, grid_row);
    }

    function bind_mapping_row_events(frm, row, grid_row) {
        const state = get_palette_state(frm);
        [
            "country_field",
            "state_field",
            "division_field",
            "district_field",
            "subdistrict_field",
            "town_field",
            "city_field",
            "zip_code_field",
            "address_line_1_field",
            "address_line_2_field",
            "latitude_field",
            "longitude_field",
            "place_id_field",
            "map_view_field",
            "region_field",
            "geofence_radius_field",
            "geofence_center_lat_field",
            "geofence_center_lng_field",
        ].forEach(function (fieldname) {
            const field = grid_row.fields_dict && grid_row.fields_dict[fieldname];
            if (!field || !field.$input || field.__erpmax_geo_target_bound) return;
            field.__erpmax_geo_target_bound = true;
            field.$input.on("mousedown click", function (e) {
                e.stopPropagation();
            });
            field.$input.on("focusin", function () {
                state.active = { cdt: row.doctype, cdn: row.name, fieldname: fieldname };
                render_palette_for_settings(frm);
            });
        });
    }

    function patch_geo_gridrow_toggle_view(frm) {
        const grid = frm && frm.fields_dict && frm.fields_dict.doctype_mappings && frm.fields_dict.doctype_mappings.grid;
        if (!grid) return;

        const grid_wrapper = grid.wrapper;
        if (grid_wrapper && !grid_wrapper.data("erpmaxGeoGridCaptureGuard")) {
            grid_wrapper.data("erpmaxGeoGridCaptureGuard", true);
            const el = grid_wrapper.get(0);
            if (el && el.addEventListener) {
                el.addEventListener("click", function (e) {
                    if (e.target && e.target.closest && e.target.closest(".grid-form-heading, .grid-footer-toolbar")) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
                    }
                }, true);
            }
        }

        const sample_row =
            (grid.grid_rows_by_docname && Object.values(grid.grid_rows_by_docname)[0]) ||
            (grid.grid_rows && Object.values(grid.grid_rows)[0]) ||
            null;
        const proto = sample_row && sample_row.constructor && sample_row.constructor.prototype;
        if (!proto || proto.__erpmax_geo_toggle_view_patched) return;

        proto.__erpmax_geo_toggle_view_patched = true;
        proto.toggle_view = function () {
            const parent_options = this.grid && this.grid.df && this.grid.df.options;
            const parent_fieldname = this.grid && this.grid.df && this.grid.df.fieldname;
            if (parent_options === "Geo Field Mapping" || parent_fieldname === "doctype_mappings" || this.doctype === "Geo Field Mapping") {
                return;
            }
        };

        (grid.grid_rows_by_docname ? Object.values(grid.grid_rows_by_docname) : []).forEach(function (row) {
            if (row) row.toggle_view = proto.toggle_view;
        });
    }

    function apply_mapping_suggestions(frm, mapping_row) {
        if (!mapping_row || !mapping_row.target_doctype) return;
        frappe.call({
            method: "erpmax.erpmax_geo.registry.suggest_geo_field_mapping",
            args: { doctype: mapping_row.target_doctype },
            callback: function (r) {
                const suggestion = r.message || {};
                const state = get_palette_state(frm);
                state.suggestions = suggestion;
                Object.keys(suggestion).forEach(function (key) {
                    const fieldname = key + "_field";
                    const field_value = mapping_row[fieldname];
                    const valid_options = (state.fields || []).map(function (item) { return item.fieldname; });
                    const is_valid = field_value && valid_options.indexOf(field_value) !== -1;
                    const suggested_value = suggestion[key] && suggestion[key].fieldname ? suggestion[key].fieldname : "";
                    if ((!field_value || !is_valid) && suggested_value) {
                        frappe.model.set_value(mapping_row.doctype, mapping_row.name, fieldname, suggested_value);
                    }
                });
                frm.refresh_field("doctype_mappings");
                render_palette_for_settings(frm);
            },
        });
    }

    function update_settings_field_preview(frm, target_doctype_name) {
        if (!target_doctype_name || !has_field(frm, "doctype_fields_html")) return;
        frappe.call({
            method: "erpmax.erpmax_geo.registry.get_doctype_fields",
            args: { doctype: target_doctype_name },
            callback: function (r) {
                const fields = r.message || [];
                const html = render_relevant_fields_html(fields);
                set_geo_settings_html(frm, "doctype_fields_html", html);
                const state = get_palette_state(frm);
                state.doctype = target_doctype_name;
                state.fields = fields;
                state.active = null;
                const mapping_row = (frm.doc.doctype_mappings || []).find(function (item) { return item.target_doctype === target_doctype_name; });
                if (mapping_row) apply_row_field_options(frm, mapping_row, fields);
                patch_geo_gridrow_toggle_view(frm);
                render_settings_layout(frm);
                render_palette_for_settings(frm);
            },
        });
    }

    function sync_geo_settings_provider(frm) {
        const provider = get_value(frm, "map_provider") || Geo.get_setting("map_provider", "Leaflet");
        const google_visible = provider === "Google";
        ["google_maps_api_key", "google_places_api_key"].forEach(function (fieldname) {
            set_visible_if_present(frm, fieldname, google_visible);
            if (!google_visible) clear_value(frm, fieldname);
        });
        ["default_radius_m", "autocomplete_bias_radius_m", "minimum_address_level", "clamp_marker_to_boundary", "fallback_to_osm", "require_place_id"].forEach(function (fieldname) {
            set_visible_if_present(frm, fieldname, true);
        });
        if (has_field(frm, "mapping_help_html")) {
            set_visible_if_present(frm, "mapping_help_html", true);
        }
        if (has_field(frm, "doctype_fields_html")) {
            set_visible_if_present(frm, "doctype_fields_html", true);
        }
        if (has_field(frm, "field_palette_html")) {
            set_visible_if_present(frm, "field_palette_html", true);
        }
    }

    function ensure_geo_settings_view(frm) {
        if (!frm || !is_geo_settings_form(frm)) return;
        sync_geo_settings_provider(frm);
        render_settings_layout(frm);
        const rows = frm.doc.doctype_mappings || [];
        const first = rows.find(function (mapping_row) { return mapping_row.target_doctype; });
        if (first) {
            update_settings_field_preview(frm, first.target_doctype);
        }
    }

    function setup_geo_settings_form(frm) {
        sync_geo_settings_provider(frm);
        frm.set_df_property && frm.set_df_property("doctype_mappings", "in_place_edit", 1);
        if (frm.fields_dict && frm.fields_dict.doctype_mappings && frm.fields_dict.doctype_mappings.grid) {
            frm.fields_dict.doctype_mappings.grid.editable_grid = true;
            const grid_wrapper = frm.fields_dict.doctype_mappings.grid.wrapper;
            if (grid_wrapper && !grid_wrapper.data("erpmaxGeoGridGuard")) {
                grid_wrapper.data("erpmaxGeoGridGuard", true);
                grid_wrapper.on("click mousedown", ".grid-form-heading, .grid-footer-toolbar, .grid-row-check, .sortable-handle", function (e) {
                    e.stopPropagation();
                });
            }
        }
        frm.refresh_field && frm.refresh_field("doctype_mappings");
        patch_geo_gridrow_toggle_view(frm);
        render_settings_layout(frm);
        frm.set_query && frm.set_query("target_doctype", "doctype_mappings", function () {
            return {
                query: "erpmax.erpmax_geo.registry.search_geo_doctypes",
            };
        });
        bind_input_once(frm, "map_provider", "change input", function () {
            sync_geo_settings_provider(frm);
        });

        bind_input_once(frm, "google_maps_api_key", "change input", function () {
            sync_geo_settings_provider(frm);
        });
        bind_input_once(frm, "google_places_api_key", "change input", function () {
            sync_geo_settings_provider(frm);
        });

        bind_input_once(frm, "doctype", "change input", function () {
            const state = get_palette_state(frm);
            state.doctype = get_value(frm, "doctype");
            state.active = null;
            render_settings_layout(frm);
            render_palette_for_settings(frm);
        });

        if (has_field(frm, "doctype_fields_html") && frm.doc.doctype_mappings && frm.doc.doctype_mappings.length) {
            const first = frm.doc.doctype_mappings.find(function (mapping_row) { return mapping_row.target_doctype; });
            if (first) update_settings_field_preview(frm, first.target_doctype);
        }

        (frm.doc.doctype_mappings || []).forEach(function (mapping_row) {
            if (mapping_row.target_doctype) {
                frappe.call({
                    method: "erpmax.erpmax_geo.registry.get_doctype_fields",
                    args: { doctype: mapping_row.target_doctype },
                    callback: function (r) {
                        const fields = r.message || [];
                        apply_row_field_options(frm, mapping_row, fields);
                        get_palette_state(frm).fields = fields;
                        apply_mapping_suggestions(frm, mapping_row);
                    },
                });
            }
        });

        render_palette_for_settings(frm);

    }

    function on_geo_field_mapping_add(frm, cdt, cdn) {
        const state = get_palette_state(frm);
        state.active = null;
        state.query = "";
        patch_geo_gridrow_toggle_view(frm);
        render_palette_for_settings(frm);
    }

    function on_country_change(frm) {
        clear_value(frm, "state");
        clear_value(frm, "city");
        clear_value(frm, "region");
        apply_country_context(frm);
    }

    Geo.init_form = function (frm) {
        if (should_skip_form(frm)) return;

        var run = function () {
            if (should_skip_form(frm)) return;
            if (is_geo_settings_form(frm)) {
                setup_geo_settings_form(frm);
                return;
            }
            setup_geo_fields(frm);
            bind_geo_events(frm);
            init_map(frm);
            apply_country_context(frm);
            update_map_boundary(frm);
            update_map_view(frm);
        };

        if (frm.__erpmax_geo_init_started) {
            return frm.__erpmax_geo_init_started.then(run);
        }

        frm.__erpmax_geo_init_started = Geo.load_config(frm.doctype).then(function () {
            return run();
        }).then(function () {
            frm.__erpmax_geo_init_started = null;
        }, function (error) {
            frm.__erpmax_geo_init_started = null;
            throw error;
        });

        return frm.__erpmax_geo_init_started;
    };

    Geo.on_country_change = on_country_change;
    Geo.on_state_change = function (frm) {
        clear_value(frm, "city");
        Geo.sync_region(frm, false);
        refresh_region_hints(frm);
        Geo.update_map_boundary(frm);
    };

    Geo.on_address_part_change = function (frm) {
        refresh_region_hints(frm);
        return Geo.sync_region(frm, false);
    };

    Geo.create_region = function (frm) {
        if (!frm || !get_country(frm) || !frm.doc || !frm.doc.name || frm.doc.__islocal) return Promise.resolve();
        return frappe.call({
            method: "erpmax.erpmax_geo.registry.bulk_resolve_region",
            args: { doctype: frm.doctype, names: JSON.stringify([frm.doc.name]), create: 1 },
            freeze: true,
            freeze_message: __("Creating region..."),
        }).then(function () {
            if (has_field(frm, "region")) frm.refresh_field("region");
            frappe.show_alert({ message: __("Region synced"), indicator: "green" });
        });
    };

    Geo.validate = function (frm) {
        return frappe.call({
            method: "erpmax.erpmax_geo.registry.validate_address_profile",
            args: {
                country: get_country(frm),
                doc: frm.doc,
            },
        }).then((r) => {
            const result = r.message || {};
            if (!result.valid) {
                const parts = [];
                if (result.missing && result.missing.length) parts.push("Missing: " + result.missing.join(", "));
                if (result.invalid && result.invalid.length) parts.push("Invalid: " + result.invalid.map((x) => x.fieldname).join(", "));
                frappe.throw(parts.join(" | ") || "Address validation failed");
            }
            return Geo.sync_region(frm, false).then(() => result);
        });
    };

    Geo.init_map = function (frm) {
        init_map(frm);
    };

    Geo.update_map_view = function (frm) {
        update_map_view(frm);
    };

    Geo.update_map_boundary = function (frm) {
        update_map_boundary(frm);
    };

    Geo.remove_map = function (frm) {
        remove_map(frm);
    };

    frappe.ui.form.on("Geo Field Mapping", {
        target_doctype(frm, cdt, cdn) {
            const mapping_row = locals[cdt][cdn];
            if (!mapping_row || !mapping_row.target_doctype) return;
            const state = get_palette_state(frm);
            state.active = { cdt: cdt, cdn: cdn, fieldname: "country_field" };
            frappe.call({
                method: "erpmax.erpmax_geo.registry.get_doctype_fields",
                args: { doctype: mapping_row.target_doctype },
                callback: function (r) {
                    const fields = r.message || [];
                    update_settings_field_preview(frm, mapping_row.target_doctype);
                    apply_row_field_options(frm, mapping_row, fields);
                    apply_mapping_suggestions(frm, mapping_row);
                },
            });
        },
    });

    Geo.setup_address_autocomplete = function (frm) {
        if (frm.__erpmax_geo_addr_ac) return;
        frm.__erpmax_geo_addr_ac = true;
        const addr_field = field(frm, "address_line_1");
        if (!addr_field || !addr_field.$input) return;
        let timer = null;
        addr_field.$input.on("input", function () {
            clearTimeout(timer);
            const q = (this.value || "").trim();
            if (q.length < 3) return hide_suggestions();
            timer = setTimeout(function () {
                frappe.call({
                    method: "erpmax.erpmax_geo.registry.search_places",
                    args: { query: q, country: get_country(frm), doc: frm.doc, limit: 8 },
                    callback: function (r) {
                        const results = r.message || [];
                        render_suggestions(addr_field.$input.get(0), results.map(function (d) {
                            return { value: d.display_name, label: d.display_name, data: d };
                        }), function (row) {
                            const d = row.data || {};
                            if (has_field(frm, "address_line_1")) set_value(frm, "address_line_1", [d.house_number, d.road].filter(Boolean).join(", ") || d.display_name.split(",")[0].trim());
                            if (d.city) set_value(frm, "city", d.city);
                            if (d.state) set_value(frm, "state", d.state);
                            if (d.postcode) set_value(frm, "zip_code", d.postcode);
                            if (d.lat && d.lon) {
                                set_value(frm, "latitude", d.lat);
                                set_value(frm, "longitude", d.lon);
                                const m = get_map(frm);
                                if (m) {
                                    m._marker.setLatLng([d.lat, d.lon]);
                                    m._map.setView([d.lat, d.lon], 15);
                                }
                            }
                            if (has_field(frm, "region")) Geo.sync_region(frm, false);
                        });
                    },
                });
            }, 400);
        });
        addr_field.$input.on("blur", function () { setTimeout(hide_suggestions, 200); });
    };

    Geo.sync_region = function (frm, create) {
        if (!frm || !has_field(frm, "region") || !get_country(frm)) return Promise.resolve();
        return frappe.call({
            method: "erpmax.erpmax_geo.registry.resolve_region",
            args: {
                country: get_country(frm),
                company: get_value(frm, "company") || frm.doc.name || "",
                doc: frm.doc,
                create: create ? 1 : 0,
            },
        }).then((r) => {
            const result = r.message || {};
            if (result.region) {
                return set_value(frm, "region", result.region);
            }
        });
    };

    function get_checked_docnames(listview) {
        const rows = (listview && listview.get_checked_items && listview.get_checked_items()) || [];
        return rows.map(function (row) { return row.name; }).filter(Boolean);
    }

    function bulk_create_regions(listview) {
        const names = get_checked_docnames(listview);
        if (!names.length) {
            frappe.msgprint({ message: __("Select at least one record."), indicator: "orange" });
            return;
        }
        frappe.call({
            method: "erpmax.erpmax_geo.registry.bulk_resolve_region",
            args: { doctype: listview.doctype, names: JSON.stringify(names), create: 1 },
            freeze: true,
            freeze_message: __("Creating regions..."),
        }).then(function (r) {
            const result = r.message || {};
            frappe.show_alert({
                message: __("Regions processed: {0}", [result.processed || 0]),
                indicator: "green",
            });
            if (listview && listview.refresh) listview.refresh();
        });
    }

    function auto_boot() {
        patch_form_refresh();
        const frm = window.cur_frm;
        if (!frm || should_skip_form(frm)) return;
        if (frm.doctype === "Geo" || frm.doctype === "Geo Settings") {
            patch_geo_gridrow_toggle_view(frm);
        }
        Geo.init_form(frm);
    }

    if (!window.__erpmax_geo_bootstrapped) {
        window.__erpmax_geo_bootstrapped = true;
        if (window.frappe && frappe.after_ajax) {
            frappe.after_ajax(auto_boot);
        }
        setInterval(function () {
            const frm = window.cur_frm;
            if (frm && (frm.doctype === "Geo" || frm.doctype === "Geo Settings")) {
                patch_geo_gridrow_toggle_view(frm);
            }
        }, 1000);
        setInterval(auto_boot, 1000);
        setTimeout(auto_boot, 0);
    }

    frappe.ui.form.on("Geo Settings", {
        refresh(frm) {
            setTimeout(function () {
                ensure_geo_settings_view(frm);
            }, 0);
            setTimeout(function () {
                ensure_geo_settings_view(frm);
            }, 400);
        },
        onload_post_render(frm) {
            setTimeout(function () {
                ensure_geo_settings_view(frm);
            }, 0);
        },
        doctype_mappings_add(frm) {
            setTimeout(function () {
                ensure_geo_settings_view(frm);
            }, 0);
        },
    });

    frappe.ui.form.on("Geo Settings", {
        doctype_mappings_add: on_geo_field_mapping_add,
    });

    frappe.ui.form.on("Geo", {
        doctype_mappings_add: on_geo_field_mapping_add,
    });

    function add_region_actions(frm) {
        if (!frm || !["Address", "Customer"].includes(frm.doctype) || frm.__erpmax_region_actions_added) return;
        frm.__erpmax_region_actions_added = true;
        if (frm.add_custom_button) {
            frm.add_custom_button(__("Create Region"), function () {
                Geo.create_region(frm).then(function () {
                    frm.refresh_field && frm.refresh_field("region");
                });
            }, __("Region"));
        }
    }

    frappe.ui.form.on("Address", {
        refresh: add_region_actions,
        onload_post_render: add_region_actions,
    });

    frappe.ui.form.on("Customer", {
        refresh: add_region_actions,
        onload_post_render: add_region_actions,
    });

    function setup_region_listview(doctype) {
        frappe.listview_settings = frappe.listview_settings || {};
        frappe.listview_settings[doctype] = frappe.listview_settings[doctype] || {};
        const existing_onload = frappe.listview_settings[doctype].onload;
        frappe.listview_settings[doctype].onload = function (listview) {
            if (existing_onload) existing_onload(listview);
            if (listview.__erpmaxRegionActionBound) return;
            listview.__erpmaxRegionActionBound = true;
            if (listview.page && listview.page.add_action_item) {
                listview.page.add_action_item(__("Create Regions"), function () {
                    bulk_create_regions(listview);
                });
            }
        };
    }

    setup_region_listview("Address");
    setup_region_listview("Customer");

    window.erpmax_geo = Geo;
})();
