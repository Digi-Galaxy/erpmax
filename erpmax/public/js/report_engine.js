/**
 * ERPMax Report Engine - Stimulsoft-like reporting
 * Comprehensive report builder and viewer
 */

frappe.provide('erpmax.report_engine');

erpmax.report_engine = {
    // Report templates
    templates: {},

    // Current report state
    currentReport: null,

    /**
     * Initialize report engine
     */
    init: function() {
        this.load_templates();
        this.bind_events();
    },

    /**
     * Load report templates
     */
    load_templates: function() {
        this.templates = {
            'financial': {
                name: 'Financial Report',
                type: 'financial',
                sections: ['header', 'filters', 'data', 'summary', 'charts']
            },
            'sales': {
                name: 'Sales Report',
                type: 'sales',
                sections: ['header', 'filters', 'data', 'summary', 'charts']
            },
            'purchase': {
                name: 'Purchase Report',
                type: 'purchase',
                sections: ['header', 'filters', 'data', 'summary', 'charts']
            },
            'inventory': {
                name: 'Inventory Report',
                type: 'inventory',
                sections: ['header', 'filters', 'data', 'summary']
            },
            'custom': {
                name: 'Custom Report',
                type: 'custom',
                sections: ['header', 'filters', 'data']
            }
        };
    },

    /**
     * Bind events
     */
    bind_events: function() {
        $(document).on('click', '.report-export-pdf', this.export_pdf.bind(this));
        $(document).on('click', '.report-export-excel', this.export_excel.bind(this));
        $(document).on('click', '.report-export-csv', this.export_csv.bind(this));
        $(document).on('click', '.report-print', this.print_report.bind(this));
    },

    /**
     * Create a new report
     */
    createReport: function(config) {
        const report = {
            id: 'report_' + Date.now(),
            name: config.name || 'Untitled Report',
            type: config.type || 'custom',
            data: config.data || [],
            columns: config.columns || [],
            filters: config.filters || [],
            groups: config.groups || [],
            sorts: config.sorts || [],
            summaries: config.summaries || [],
            charts: config.charts || [],
            layout: config.layout || {},
            created: new Date(),
            modified: new Date()
        };

        this.currentReport = report;
        return report;
    },

    /**
     * Render report to HTML
     */
    renderReport: function(report, container) {
        let html = '<div class="erpmax-report">';

        // Header section
        html += this.renderHeader(report);

        // Filters section
        if (report.filters.length > 0) {
            html += this.renderFilters(report);
        }

        // Data section
        html += this.renderData(report);

        // Summary section
        if (report.summaries.length > 0) {
            html += this.renderSummary(report);
        }

        // Charts section
        if (report.charts.length > 0) {
            html += this.renderCharts(report);
        }

        // Footer section
        html += this.renderFooter(report);

        html += '</div>';

        $(container).html(html);
        this.initCharts(report);
    },

    /**
     * Render report header
     */
    renderHeader: function(report) {
        return `
            <div class="report-header">
                <div class="report-title">
                    <h2>${report.name}</h2>
                    <p class="report-subtitle">${report.type.toUpperCase()} REPORT</p>
                </div>
                <div class="report-meta">
                    <span>Generated: ${frappe.datetime.str_to_user(report.created)}</span>
                    <span>Page: 1 of 1</span>
                </div>
                <div class="report-actions no-print">
                    <button class="btn btn-sm btn-default report-print">
                        <i class="fa fa-print"></i> Print
                    </button>
                    <button class="btn btn-sm btn-default report-export-pdf">
                        <i class="fa fa-file-pdf-o"></i> PDF
                    </button>
                    <button class="btn btn-sm btn-default report-export-excel">
                        <i class="fa fa-file-excel-o"></i> Excel
                    </button>
                    <button class="btn btn-sm btn-default report-export-csv">
                        <i class="fa fa-file-text-o"></i> CSV
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render report filters
     */
    renderFilters: function(report) {
        let html = '<div class="report-filters">';
        html += '<h4>Filters</h4>';
        html += '<div class="filter-row">';

        report.filters.forEach(filter => {
            html += `
                <div class="filter-group">
                    <label>${filter.label}</label>
                    <input type="${filter.type || 'text'}" 
                           class="form-control form-control-sm" 
                           value="${filter.value || ''}"
                           placeholder="${filter.placeholder || ''}">
                </div>
            `;
        });

        html += '</div></div>';
        return html;
    },

    /**
     * Render report data table
     */
    renderData: function(report) {
        if (!report.data || report.data.length === 0) {
            return '<div class="report-no-data">No data available</div>';
        }

        let html = '<div class="report-data">';
        html += '<table class="table table-bordered table-sm">';

        // Table header
        html += '<thead><tr>';
        report.columns.forEach(col => {
            html += `<th style="width:${col.width || 'auto'}; text-align:${col.align || 'left'}">${col.label}</th>`;
        });
        html += '</tr></thead>';

        // Table body
        html += '<tbody>';
        report.data.forEach((row, idx) => {
            html += '<tr>';
            report.columns.forEach(col => {
                let value = row[col.field] || '';
                if (col.formatter) {
                    value = col.formatter(value, row);
                }
                html += `<td style="text-align:${col.align || 'left'}">${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody>';

        // Table footer with totals
        if (report.summaries.length > 0) {
            html += '<tfoot><tr>';
            report.columns.forEach((col, idx) => {
                if (idx === 0) {
                    html += '<th>Total</th>';
                } else {
                    const summary = report.summaries.find(s => s.field === col.field);
                    if (summary) {
                        const total = this.calculateSummary(report.data, col.field, summary.type);
                        html += `<th style="text-align:${col.align || 'right'}">${this.formatNumber(total)}</th>`;
                    } else {
                        html += '<th></th>';
                    }
                }
            });
            html += '</tr></tfoot>';
        }

        html += '</table></div>';
        return html;
    },

    /**
     * Render report summary
     */
    renderSummary: function(report) {
        let html = '<div class="report-summary">';
        html += '<h4>Summary</h4>';
        html += '<div class="summary-cards">';

        report.summaries.forEach(summary => {
            const value = this.calculateSummary(report.data, summary.field, summary.type);
            html += `
                <div class="summary-card">
                    <div class="summary-label">${summary.label}</div>
                    <div class="summary-value">${this.formatNumber(value)}</div>
                </div>
            `;
        });

        html += '</div></div>';
        return html;
    },

    /**
     * Render report charts
     */
    renderCharts: function(report) {
        let html = '<div class="report-charts">';
        html += '<h4>Charts</h4>';
        html += '<div class="charts-grid">';

        report.charts.forEach((chart, idx) => {
            html += `<div class="chart-container" id="chart_${report.id}_${idx}"></div>`;
        });

        html += '</div></div>';
        return html;
    },

    /**
     * Render report footer
     */
    renderFooter: function(report) {
        return `
            <div class="report-footer">
                <div class="footer-left">
                    <p>ERPMax - ERP System</p>
                </div>
                <div class="footer-right">
                    <p>Page 1 of 1</p>
                </div>
            </div>
        `;
    },

    /**
     * Calculate summary value
     */
    calculateSummary: function(data, field, type) {
        const values = data.map(row => parseFloat(row[field]) || 0);

        switch(type) {
            case 'sum':
                return values.reduce((a, b) => a + b, 0);
            case 'avg':
                return values.reduce((a, b) => a + b, 0) / values.length;
            case 'count':
                return values.length;
            case 'min':
                return Math.min(...values);
            case 'max':
                return Math.max(...values);
            default:
                return values.reduce((a, b) => a + b, 0);
        }
    },

    /**
     * Format number
     */
    formatNumber: function(num, decimals = 2) {
        return parseFloat(num).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    /**
     * Initialize charts in report
     */
    initCharts: function(report) {
        report.charts.forEach((chart, idx) => {
            const containerId = `chart_${report.id}_${idx}`;
            const container = document.getElementById(containerId);

            if (container) {
                const chartData = this.prepareChartData(report.data, chart);
                erpmax.charts[`create${chart.type}Chart`](`#${containerId}`, chartData, {
                    title: chart.title
                });
            }
        });
    },

    /**
     * Prepare chart data from report data
     */
    prepareChartData: function(data, chartConfig) {
        const categories = [...new Set(data.map(row => row[chartConfig.categoryField]))];
        const seriesData = categories.map(cat => {
            return data
                .filter(row => row[chartConfig.categoryField] === cat)
                .reduce((sum, row) => sum + (parseFloat(row[chartConfig.valueField]) || 0), 0);
        });

        return {
            categories: categories,
            series: [{
                name: chartConfig.seriesName || 'Value',
                data: seriesData
            }]
        };
    },

    /**
     * Export report as PDF
     */
    export_pdf: function() {
        const reportContent = document.querySelector('.erpmax-report');
        if (reportContent) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Report</title>
                    <link rel="stylesheet" href="/assets/frappe/css/frappe.css">
                    <link rel="stylesheet" href="/assets/erpmax/css/erpmax.bundle.css">
                    <style>
                        .report-header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
                        .report-title h2 { margin: 0; }
                        .report-meta { color: #666; font-size: 12px; }
                        .report-actions { display: none; }
                        .no-print { display: none; }
                        .table { width: 100%; border-collapse: collapse; }
                        .table th, .table td { border: 1px solid #ddd; padding: 8px; }
                        .table th { background-color: #f5f5f5; }
                        .report-summary { margin-top: 20px; }
                        .summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
                        .summary-card { border: 1px solid #ddd; padding: 10px; text-align: center; }
                        .summary-label { color: #666; font-size: 12px; }
                        .summary-value { font-size: 18px; font-weight: bold; }
                        .report-footer { margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; display: flex; justify-content: space-between; }
                    </style>
                </head>
                <body>
                    ${reportContent.innerHTML}
                    <script>window.print();window.close();<\/script>
                </body>
                </html>
            `);
            printWindow.document.close();
        }
    },

    /**
     * Export report as Excel
     */
    export_excel: function() {
        if (!this.currentReport) return;

        let csv = this.generateCSV();
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${this.currentReport.name}.csv`;
        link.click();
    },

    /**
     * Export report as CSV
     */
    export_csv: function() {
        this.export_excel();
    },

    /**
     * Generate CSV content
     */
    generateCSV: function() {
        if (!this.currentReport) return '';

        const report = this.currentReport;
        let csv = '';

        // Headers
        csv += report.columns.map(col => `"${col.label}"`).join(',') + '\n';

        // Data rows
        report.data.forEach(row => {
            csv += report.columns.map(col => {
                let value = row[col.field] || '';
                return `"${value}"`;
            }).join(',') + '\n';
        });

        // Summary row
        if (report.summaries.length > 0) {
            csv += '"Total",';
            report.columns.slice(1).forEach((col, idx) => {
                const summary = report.summaries.find(s => s.field === col.field);
                if (summary) {
                    const total = this.calculateSummary(report.data, col.field, summary.type);
                    csv += `"${total}"`;
                } else {
                    csv += '""';
                }
                if (idx < report.columns.length - 2) csv += ',';
            });
            csv += '\n';
        }

        return csv;
    },

    /**
     * Print report
     */
    print_report: function() {
        window.print();
    }
};

// Initialize report engine
$(document).ready(function() {
    erpmax.report_engine.init();
});

// Make globally available
window.erpmax_report_engine = erpmax.report_engine;
