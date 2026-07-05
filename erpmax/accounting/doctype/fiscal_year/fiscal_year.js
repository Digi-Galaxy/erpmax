frappe.ui.form.on("Fiscal Year", {
    year_start_date: function(frm) {
        _auto_fill_end_date(frm);
    },
    
    time_span: function(frm) {
        _auto_fill_end_date(frm);
    }
});

function _auto_fill_end_date(frm) {
    if (!frm.doc.year_start_date || !frm.doc.time_span) return;
    
    const start = new Date(frm.doc.year_start_date);
    let end = new Date(start);
    
    switch (frm.doc.time_span) {
        case "1 Month":
            end.setMonth(end.getMonth() + 1);
            end.setDate(end.getDate() - 1);
            break;
        case "3 Months":
            end.setMonth(end.getMonth() + 3);
            end.setDate(end.getDate() - 1);
            break;
        case "6 Months":
            end.setMonth(end.getMonth() + 6);
            end.setDate(end.getDate() - 1);
            break;
        case "Short Year":
            end.setFullYear(end.getFullYear() + 1);
            end.setDate(end.getDate() - 1);
            frm.set_value("is_short_year", 1);
            break;
        case "Long Year":
            end.setFullYear(end.getFullYear() + 1);
            end.setDate(end.getDate() - 1);
            frm.set_value("is_short_year", 0);
            break;
    }
    
    frm.set_value("year_end_date", frappe.datetime.get_dump(end));
}
