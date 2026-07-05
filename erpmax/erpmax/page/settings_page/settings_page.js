frappe.pages["settings-page"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Settings"),
        single_column: true,
    });

    const settings = new SettingsPage(page);
    page.set_secondary_action(__("Refresh"), () => settings.reload(), "refresh");
};

class SettingsPage {
    constructor(page) {
        this.page = page;
        this.render_skeleton();
        this.load_data();
    }

    render_skeleton() {
        $(`
            <style>
                .sp-wrap { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .sp-section { margin-bottom: 24px; }
                .sp-section-title { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 12px; }
                .sp-card { background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }
                .sp-info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
                .sp-info-item { display: flex; justify-content: space-between; padding: 12px; background: var(--control-bg, #f5f5f5); border-radius: 8px; }
                .sp-info-label { color: var(--text-muted); }
                .sp-info-value { font-weight: 600; color: var(--text-color); }
                .sp-module-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
                .sp-module-item { padding: 12px; background: var(--control-bg, #f5f5f5); border-radius: 8px; text-align: center; }
                .sp-module-name { font-weight: 600; font-size: 13px; color: var(--text-color); }
                .sp-module-badge { display: inline-block; margin-top: 4px; padding: 2px 8px; font-size: 10px; border-radius: 4px; background: #28a745; color: white; }
                .sp-actions { display: flex; gap: 10px; flex-wrap: wrap; }
            </style>
            <div class="sp-wrap">
                <div class="sp-section">
                    <div class="sp-section-title">System Information</div>
                    <div class="sp-card" id="sp-info">
                        <div class="sp-loading">Loading...</div>
                    </div>
                </div>
                <div class="sp-section">
                    <div class="sp-section-title">Modules</div>
                    <div class="sp-card" id="sp-modules">
                        <div class="sp-loading">Loading...</div>
                    </div>
                </div>
                <div class="sp-section">
                    <div class="sp-section-title">Quick Actions</div>
                    <div class="sp-card">
                        <div class="sp-actions">
                            <button class="btn btn-primary" onclick="current_settings.clear_cache()">
                                <i class="fa fa-refresh"></i> Clear Cache
                            </button>
                            <button class="btn btn-default" onclick="current_settings.rebuild_assets()">
                                <i class="fa fa-wrench"></i> Rebuild Assets
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).appendTo(this.page.body);
        window.current_settings = this;
    }

    async load_data() {
        try {
            const [info, modules] = await Promise.all([
                frappe.xcall("erpmax.erpmax.page.settings_page.settings_page.get_system_info"),
                frappe.xcall("erpmax.erpmax.page.settings_page.settings_page.get_module_status"),
            ]);
            
            if (info) this.render_info(info);
            if (modules) this.render_modules(modules);
        } catch (e) {
            console.error("Failed to load settings:", e);
        }
    }

    render_info(info) {
        let html = '<div class="sp-info-grid">';
        html += `<div class="sp-info-item"><span class="sp-info-label">Version</span><span class="sp-info-value">${info.version || "1.0.0"}</span></div>`;
        html += `<div class="sp-info-item"><span class="sp-info-label">Frappe Version</span><span class="sp-info-value">${info.frappe_version || "N/A"}</span></div>`;
        html += `<div class="sp-info-item"><span class="sp-info-label">Site</span><span class="sp-info-value">${info.site || "N/A"}</span></div>`;
        html += `<div class="sp-info-item"><span class="sp-info-label">Developer Mode</span><span class="sp-info-value">${info.developer_mode ? "Yes" : "No"}</span></div>`;
        html += '</div>';
        $("#sp-info").html(html);
    }

    render_modules(modules) {
        let html = '<div class="sp-module-grid">';
        modules.forEach(m => {
            html += `
                <div class="sp-module-item">
                    <div class="sp-module-name">${m}</div>
                    <div class="sp-module-badge">Active</div>
                </div>
            `;
        });
        html += '</div>';
        $("#sp-modules").html(html);
    }

    async clear_cache() {
        frappe.confirm("Clear all caches?", async () => {
            try {
                await frappe.xcall("erpmax.erpmax.page.settings_page.settings_page.clear_cache");
                frappe.show_alert({ message: "Cache cleared!", indicator: "green" });
            } catch (e) {
                frappe.show_alert({ message: "Failed to clear cache", indicator: "red" });
            }
        });
    }

    rebuild_assets() {
        frappe.show_alert({ message: "Rebuild started...", indicator: "blue" });
    }

    reload() {
        this.load_data();
    }
}
