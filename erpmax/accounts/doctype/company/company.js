frappe.ui.form.on("Company", {
  setup(frm) {
    frm.set_query("parent_company", () => ({
      filters: { is_group: 1 },
    }));
  },

  company_name(frm) {
    if (frm.doc.__islocal && frm.doc.company_name && !frm.doc.abbreviation) {
      const abbr = frm.doc.company_name
        .split(/\s+/)
        .filter(Boolean)
        .map((part) => part[0])
        .join("")
        .slice(0, 10)
        .toUpperCase();
      frm.set_value("abbreviation", abbr);
    }
  },

  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Company Tree"), () => {
        frappe.set_route("Tree", "Company");
      });

      if (frappe.user.has_role("System Manager") && frm.has_perm("write")) {
        frm.add_custom_button(
          __("Configure Features"),
          () => {
            frappe.prompt(
              [
                {
                  fieldtype: "Select",
                  fieldname: "feature_tier",
                  label: __("Feature Tier"),
                  reqd: 1,
                  options: "Small Company\nMedium Company\nAdvanced Enterprise",
                  default: frm.doc.feature_tier || "Small Company",
                },
              ],
              (values) => {
                frappe.call({
                  method: "erpmax.accounts.doctype.company.company.apply_feature_profile",
                  args: {
                    company: frm.doc.name,
                    feature_tier: values.feature_tier,
                  },
                  freeze: true,
                  callback: () => frm.reload_doc(),
                });
              },
              __("Configure Company Features"),
              __("Apply")
            );
          },
          __("Manage")
        );

        frm.add_custom_button(
          __('Delete Transactions'),
          () => {
            frappe.verify_password(() => {
              frappe.prompt(
                {
                  fieldtype: "Data",
                  fieldname: "company_name",
                  label: __('Please enter the company name to confirm'),
                  reqd: 1,
                  description: __(
                    'Please make sure you really want to delete all the transactions for {0}. Your master data will remain. This action cannot be undone.',
                    [frappe.utils.bold(frm.doc.name)]
                  ),
                },
                (data) => {
                  if (data.company_name !== frm.doc.name) {
                    frappe.msgprint(__('Company name not same'));
                    return;
                  }
                  frappe.call({
                    method: "erpmax.accounts.doctype.company.company.create_transaction_deletion_request",
                    args: { company: frm.doc.name },
                    freeze: true,
                  });
                },
                __('Delete all the Transactions for {0}', [frappe.utils.bold(frm.doc.name)]),
                __('Delete')
              ).get_primary_btn().addClass('btn-danger');
            });
          },
          __('Manage')
        );
      }
    }
  },
});
