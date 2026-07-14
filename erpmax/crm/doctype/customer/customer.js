// Copyright (c) 2024, ERPMax and Contributors
// License: MIT. See LICENSE

frappe.ui.form.on("Customer", {
    refresh(frm) {
        // Toggle addon sections based on settings
        toggle_addon_sections(frm);
        
        // Add custom buttons
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Generate PDF'), function() {
                generate_customer_pdf(frm);
            }, __('PDF'));
            
            frm.add_custom_button(__('Create Sales Invoice'), function() {
                create_sales_invoice(frm);
            }, __('Create'));
        }
    },
    
    enable_loyalty_points(frm) {
        toggle_addon_sections(frm);
    },
    
    enable_dunning(frm) {
        toggle_addon_sections(frm);
    },
    
    enable_banking_details(frm) {
        toggle_addon_sections(frm);
    },
    
    enable_documents(frm) {
        toggle_addon_sections(frm);
    },
    
    enable_communication_log(frm) {
        toggle_addon_sections(frm);
    }
});

function toggle_addon_sections(frm) {
    // Toggle Loyalty Points section
    frm.toggle_display('sb_loyalty', frm.doc.enable_loyalty_points);
    frm.toggle_display('loyalty_program', frm.doc.enable_loyalty_points);
    frm.toggle_display('loyalty_points', frm.doc.enable_loyalty_points);
    frm.toggle_display('loyalty_currency', frm.doc.enable_loyalty_points);
    frm.toggle_display('total_points_earned', frm.doc.enable_loyalty_points);
    frm.toggle_display('total_points_redeemed', frm.doc.enable_loyalty_points);
    
    // Toggle Dunning section
    frm.toggle_display('sb_dunning', frm.doc.enable_dunning);
    frm.toggle_display('dunning_level', frm.doc.enable_dunning);
    frm.toggle_display('last_dunning_date', frm.doc.enable_dunning);
    frm.toggle_display('dunning_method', frm.doc.enable_dunning);
    frm.toggle_display('next_dunning_date', frm.doc.enable_dunning);
    frm.toggle_display('dunning_count', frm.doc.enable_dunning);
    
    // Toggle Banking Details section
    frm.toggle_display('sb_banking', frm.doc.enable_banking_details);
    frm.toggle_display('bank_name', frm.doc.enable_banking_details);
    frm.toggle_display('account_number', frm.doc.enable_banking_details);
    frm.toggle_display('iban', frm.doc.enable_banking_details);
    frm.toggle_display('swift_code', frm.doc.enable_banking_details);
    
    // Toggle Document Management section
    frm.toggle_display('sb_documents', frm.doc.enable_documents);
    frm.toggle_display('document_count', frm.doc.enable_documents);
    frm.toggle_display('last_document_date', frm.doc.enable_documents);
    
    // Toggle Communication Log section
    frm.toggle_display('sb_communication', frm.doc.enable_communication_log);
    frm.toggle_display('last_contact_date', frm.doc.enable_communication_log);
    frm.toggle_display('communication_count', frm.doc.enable_communication_log);
    frm.toggle_display('next_follow_up', frm.doc.enable_communication_log);
}

function generate_customer_pdf(frm) {
    frappe.call({
        method: "erpmax.api.pdf_generator.generate_pdf",
        args: {
            doctype: "Customer",
            docname: frm.doc.name,
            print_format: ""
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint(__('PDF generated successfully'));
            }
        }
    });
}

function create_sales_invoice(frm) {
    frappe.new_doc('Sales Invoice', {
        customer: frm.doc.name,
        customer_name: frm.doc.customer_name,
        company: frm.doc.company,
        default_currency: frm.doc.default_currency
    });
}
