/**
 * ERPMax Charts - Highcharts Integration
 * Comprehensive charting library for ERPMax
 */

frappe.provide('erpmax.charts');

erpmax.charts = {
    // Default Highcharts options
    defaultOptions: {
        chart: {
            backgroundColor: 'transparent',
            style: {
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
            }
        },
        title: {
            style: {
                fontSize: '16px',
                fontWeight: '600'
            }
        },
        credits: {
            enabled: false
        },
        exporting: {
            enabled: true,
            buttons: {
                contextButton: {
                    menuItems: ['downloadPNG', 'downloadJPEG', 'downloadPDF', 'downloadSVG', 'separator', 'downloadCSV', 'downloadXLS']
                }
            }
        },
        colors: ['#5e64ff', '#ff5858', '#28a745', '#ffc107', '#17a2b8', '#6f42c1', '#fd7e14', '#20c997']
    },

    // Chart instances storage
    charts: {},

    /**
     * Create a bar chart
     */
    createBarChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'bar',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                categories: data.categories || [],
                labels: {
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yAxis: {
                title: {
                    text: options.yAxisTitle || 'Value'
                }
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a column chart
     */
    createColumnChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'column',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                categories: data.categories || [],
                labels: {
                    rotation: -45,
                    style: {
                        fontSize: '11px'
                    }
                }
            },
            yAxis: {
                title: {
                    text: options.yAxisTitle || 'Value'
                }
            },
            plotOptions: {
                column: {
                    borderRadius: 4,
                    dataLabels: {
                        enabled: options.showLabels || false
                    }
                }
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a line chart
     */
    createLineChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'line',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                categories: data.categories || [],
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: options.yAxisTitle || 'Value'
                }
            },
            tooltip: {
                shared: true,
                crosshairs: true
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a pie chart
     */
    createPieChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'pie',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            fontSize: '12px'
                        }
                    },
                    showInLegend: options.showLegend !== false
                }
            },
            series: [{
                name: options.seriesName || 'Value',
                colorByPoint: true,
                data: data.series || []
            }],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a donut chart
     */
    createDonutChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'pie',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.1f}%)'
            },
            plotOptions: {
                pie: {
                    innerSize: '60%',
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>',
                        distance: -20,
                        style: {
                            fontSize: '12px',
                            textOutline: 'none'
                        }
                    },
                    showInLegend: options.showLegend !== false
                }
            },
            series: [{
                name: options.seriesName || 'Value',
                colorByPoint: true,
                data: data.series || []
            }],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create an area chart
     */
    createAreaChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'area',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                categories: data.categories || []
            },
            yAxis: {
                title: {
                    text: options.yAxisTitle || 'Value'
                }
            },
            tooltip: {
                shared: true,
                valueSuffix: ' units'
            },
            plotOptions: {
                area: {
                    fillOpacity: 0.5,
                    marker: {
                        radius: 2
                    }
                }
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a scatter chart
     */
    createScatterChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'scatter',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                title: {
                    text: options.xAxisTitle || 'X Axis'
                }
            },
            yAxis: {
                title: {
                    text: options.yAxisTitle || 'Y Axis'
                }
            },
            tooltip: {
                headerFormat: '<b>{series.name}</b><br>',
                pointFormat: '{point.x}, {point.y}'
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a gauge chart
     */
    createGaugeChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                type: 'solidgauge',
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            pane: {
                center: ['50%', '70%'],
                size: '140%',
                startAngle: -90,
                endAngle: 90,
                background: {
                    backgroundColor: '#EEE',
                    innerRadius: '60%',
                    outerRadius: '100%',
                    shape: 'arc'
                }
            },
            yAxis: {
                min: options.min || 0,
                max: options.max || 100,
                stops: [
                    [0.1, '#DF5353'],
                    [0.5, '#DDDF0D'],
                    [0.9, '#55BF3B']
                ],
                lineWidth: 0,
                minorTickInterval: null,
                tickAmount: 2,
                labels: {
                    y: 16
                }
            },
            series: [{
                name: options.seriesName || 'Value',
                data: data.series || [{ y: 0 }],
                dataLabels: {
                    format: '<div style="text-align:center"><span style="font-size:25px;font-weight:bold">{y:.1f}</span><span style="font-size:12px;color:#666">{series.name}</span></div>'
                }
            }],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Create a dual-axis chart
     */
    createDualAxisChart: function(selector, data, options = {}) {
        const chartOptions = {
            ...this.defaultOptions,
            chart: {
                ...this.defaultOptions.chart,
                zooming: { type: 'xy' },
                renderTo: selector
            },
            title: {
                ...this.defaultOptions.title,
                text: options.title || ''
            },
            xAxis: {
                categories: data.categories || []
            },
            yAxis: [{
                title: {
                    text: options.yAxis1Title || 'Primary'
                }
            }, {
                title: {
                    text: options.yAxis2Title || 'Secondary'
                },
                opposite: true
            }],
            tooltip: {
                shared: true
            },
            series: data.series || [],
            ...options
        };

        return Highcharts.chart(selector, chartOptions);
    },

    /**
     * Destroy a chart instance
     */
    destroyChart: function(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    },

    /**
     * Update chart data
     */
    updateChart: function(chartId, newData) {
        if (this.charts[chartId]) {
            this.charts[chartId].series[0].setData(newData, true);
        }
    },

    /**
     * Export chart as image
     */
    exportChart: function(chartId, format = 'png') {
        if (this.charts[chartId]) {
            this.charts[chartId].exportChart({
                type: `image/${format}`,
                filename: `erpmax-chart-${chartId}`
            });
        }
    }
};

// Make charts globally available
window.erpmax_charts = erpmax.charts;
