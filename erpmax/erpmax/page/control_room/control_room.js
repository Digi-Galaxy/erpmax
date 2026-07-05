frappe.pages["control-room"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Control Room"),
        single_column: true,
    });

    const dashboard = new ControlRoomDashboard(page);
    page.set_secondary_action(__("Refresh"), () => dashboard.reload(), "refresh");
};

class ControlRoomDashboard {
    constructor(page) {
        this.page = page;
        this.company = frappe.defaults.get_default("company");
        this.render_skeleton();
        this.refresh();
    }

    render_skeleton() {
        $(`
            <style>
                .cr-wrap { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .cr-kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
                .cr-kpi-card { background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; text-align: center; }
                .cr-kpi-icon { font-size: 24px; margin-bottom: 8px; }
                .cr-kpi-value { font-size: 28px; font-weight: 700; color: var(--text-color); }
                .cr-kpi-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
                .cr-stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
                .cr-stat-card { background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; text-align: center; }
                .cr-stat-value { font-size: 36px; font-weight: 700; color: var(--primary); }
                .cr-stat-label { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
                .cr-section { margin-bottom: 24px; }
                .cr-section-title { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 12px; }
                .cr-status-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
                .cr-status-item { display: flex; justify-content: space-between; padding: 12px; background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 8px; }
                .cr-status-label { color: var(--text-muted); }
                .cr-status-value { font-weight: 600; color: var(--text-color); }
                @media (max-width: 768px) {
                    .cr-kpi-grid { grid-template-columns: repeat(2, 1fr); }
                    .cr-stats-grid { grid-template-columns: 1fr; }
                }
            </style>
            <div class="cr-wrap">
                <div class="cr-kpi-grid" id="cr-kpis"></div>
                <div class="cr-stats-grid" id="cr-stats"></div>
                <div class="cr-section">
                    <div class="cr-section-title">System Status</div>
                    <div class="cr-status-grid" id="cr-status"></div>
                </div>
            </div>
        `).appendTo(this.page.body);
    }

    async refresh() {
        try {
            const r = await frappe.xcall("erpmax.erpmax.page.control_room.control_room.get_realtime_data");
            if (r) this.render_data(r);
        } catch (e) {
            console.error("Failed to load dashboard:", e);
            this.render_empty();
        }
    }

    render_data(data) {
        const d = data.dashboard || {};
        
        // KPI Cards
        const kpis = [
            { icon: "fa-line-chart", value: this.format_currency(d.total_sales || 0), label: "Total Sales (MTD)", color: "#5e64ff" },
            { icon: "fa-shopping-cart", value: this.format_currency(d.total_purchases || 0), label: "Total Purchases (MTD)", color: "#ff5858" },
            { icon: "fa-balance-scale", value: this.format_currency(d.net_profit || 0), label: "Net Profit (MTD)", color: "#28a745" },
            { icon: "fa-exclamation-triangle", value: this.format_currency(d.total_outstanding || 0), label: "Outstanding", color: "#ffc107" },
        ];
        
        let kpiHtml = "";
        kpis.forEach(kpi => {
            kpiHtml += `
                <div class="cr-kpi-card">
                    <div class="cr-kpi-icon" style="color: ${kpi.color}"><i class="fa ${kpi.icon}"></i></div>
                    <div class="cr-kpi-value">${kpi.value}</div>
                    <div class="cr-kpi-label">${kpi.label}</div>
                </div>
            `;
        });
        $("#cr-kpis").html(kpiHtml);

        // Stats
        const stats = [
            { value: d.customer_count || 0, label: "Customers" },
            { value: d.supplier_count || 0, label: "Suppliers" },
            { value: d.item_count || 0, label: "Items" },
        ];
        
        let statsHtml = "";
        stats.forEach(s => {
            statsHtml += `
                <div class="cr-stat-card">
                    <div class="cr-stat-value">${s.value}</div>
                    <div class="cr-stat-label">${s.label}</div>
                </div>
            `;
        });
        $("#cr-stats").html(statsHtml);

        // Status
        const status = data.status || {};
        let statusHtml = `
            <div class="cr-status-item">
                <span class="cr-status-label">Version</span>
                <span class="cr-status-value">${status.version || "1.0.0"}</span>
            </div>
            <div class="cr-status-item">
                <span class="cr-status-label">Last Backup</span>
                <span class="cr-status-value">${status.last_backup || "Never"}</span>
            </div>
        `;
        $("#cr-status").html(statusHtml);
    }

    render_empty() {
        $("#cr-kpis").html('<p style="text-align:center;color:var(--text-muted)">No data available</p>');
    }

    format_currency(value) {
        return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value || 0);
    }

    reload() {
        this.refresh();
    }
}
