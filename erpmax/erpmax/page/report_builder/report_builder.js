frappe.pages["report-builder"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Report Builder"),
        single_column: true,
    });

    const builder = new ReportBuilder(page);
    page.set_secondary_action(__("Refresh"), () => builder.reload(), "refresh");
};

class ReportBuilder {
    constructor(page) {
        this.page = page;
        this.render_skeleton();
        this.load_reports();
    }

    render_skeleton() {
        $(`
            <style>
                .rb-wrap { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .rb-section { margin-bottom: 24px; }
                .rb-section-title { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 12px; }
                .rb-report-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
                .rb-report-btn { background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; cursor: pointer; text-align: center; transition: all 0.15s ease; }
                .rb-report-btn:hover { border-color: var(--primary); background: var(--primary-light, #f0f0ff); }
                .rb-report-btn.active { border-color: var(--primary); background: var(--primary-light, #f0f0ff); }
                .rb-report-icon { font-size: 24px; color: var(--primary); margin-bottom: 8px; }
                .rb-report-name { font-size: 14px; font-weight: 600; color: var(--text-color); }
                .rb-output { background: var(--card-bg, #fff); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; min-height: 300px; }
                .rb-loading { text-align: center; padding: 40px; color: var(--text-muted); }
                .rb-table { width: 100%; border-collapse: collapse; }
                .rb-table th, .rb-table td { border: 1px solid var(--border-color); padding: 10px 12px; text-align: left; font-size: 13px; }
                .rb-table th { background: var(--control-bg, #f5f5f5); font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; font-size: 11px; }
                .rb-table tr:hover { background: var(--control-bg, #f5f5f5); }
                .rb-table td { font-variant-numeric: tabular-nums; }
            </style>
            <div class="rb-wrap">
                <div class="rb-section">
                    <div class="rb-section-title">Available Reports</div>
                    <div class="rb-report-grid" id="rb-reports"></div>
                </div>
                <div class="rb-section">
                    <div class="rb-section-title">Report Output</div>
                    <div class="rb-output" id="rb-output">
                        <div class="rb-loading">Select a report to generate</div>
                    </div>
                </div>
            </div>
        `).appendTo(this.page.body);
    }

    load_reports() {
        const reports = [
            { name: "trial_balance", label: "Trial Balance", icon: "fa-balance-scale" },
            { name: "general_ledger", label: "General Ledger", icon: "fa-book" },
            { name: "balance_sheet", label: "Balance Sheet", icon: "fa-file-text" },
            { name: "profit_and_loss", label: "Profit & Loss", icon: "fa-line-chart" },
            { name: "sales_register", label: "Sales Register", icon: "fa-shopping-cart" },
            { name: "purchase_register", label: "Purchase Register", icon: "fa-truck" },
            { name: "customer_summary", label: "Customer Summary", icon: "fa-users" },
            { name: "supplier_summary", label: "Supplier Summary", icon: "fa-building" },
        ];

        let html = "";
        reports.forEach(r => {
            html += `
                <div class="rb-report-btn" data-report="${r.name}" onclick="current_builder.generate_report('${r.name}')">
                    <div class="rb-report-icon"><i class="fa ${r.icon}"></i></div>
                    <div class="rb-report-name">${r.label}</div>
                </div>
            `;
        });
        $("#rb-reports").html(html);
        window.current_builder = this;
    }

    async generate_report(report_name) {
        // Highlight selected
        $(".rb-report-btn").removeClass("active");
        $(`.rb-report-btn[data-report="${report_name}"]`).addClass("active");

        // Show loading
        $("#rb-output").html('<div class="rb-loading"><i class="fa fa-spinner fa-spin"></i> Generating report...</div>');

        try {
            const r = await frappe.xcall("erpmax.erpmax.page.report_builder.report_builder.generate_report", {
                report_type: report_name
            });
            
            if (r && r.error) {
                $("#rb-output").html(`<div class="rb-loading" style="color: #dc2626">Error: ${r.error}</div>`);
            } else if (r && r.data && r.data.length > 0) {
                this.render_table(r);
            } else {
                $("#rb-output").html('<div class="rb-loading">No data found for this report</div>');
            }
        } catch (e) {
            console.error("Report error:", e);
            $("#rb-output").html(`<div class="rb-loading" style="color: #dc2626">Error: ${e.message || "Failed to generate report"}</div>`);
        }
    }

    render_table(report) {
        let html = `<div style="margin-bottom:12px;font-weight:600">${report.report_type || "Report"}</div>`;
        html += '<table class="rb-table"><thead><tr>';
        
        if (report.columns) {
            report.columns.forEach(col => {
                html += `<th>${col.label || col.fieldname || col}</th>`;
            });
        } else if (report.data && report.data.length > 0) {
            Object.keys(report.data[0]).forEach(key => {
                html += `<th>${key}</th>`;
            });
        }
        
        html += '</tr></thead><tbody>';
        
        report.data.forEach(row => {
            html += '<tr>';
            if (report.columns) {
                report.columns.forEach(col => {
                    const field = col.fieldname || col;
                    html += `<td>${row[field] !== undefined ? row[field] : ""}</td>`;
                });
            } else {
                Object.values(row).forEach(val => {
                    html += `<td>${val !== undefined ? val : ""}</td>`;
                });
            }
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        html += `<div style="margin-top:12px;font-size:12px;color:var(--text-muted)">Total: ${report.data.length} records</div>`;
        
        $("#rb-output").html(html);
    }

    reload() {
        this.load_reports();
        $("#rb-output").html('<div class="rb-loading">Select a report to generate</div>');
    }
}
