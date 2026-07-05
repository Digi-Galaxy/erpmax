frappe.treeview_settings["Account"] = {
  ignore_fields: ["parent_account"],
  get_tree_nodes: "erpmax.accounting.doctype.account.account.get_children",
  add_tree_node: "erpmax.accounting.doctype.account.account.add_node",
  filters: [
    {
      fieldname: "company",
      fieldtype: "Link",
      options: "Company",
      label: __("Company"),
      get_query: () => {
        return {
          filters: [["Company", "is_group", "=", 0]],
        };
      },
    },
  ],
  breadcrumb: "Accounts",
  root_label: "All Accounts",
  get_tree_root: false,
  menu_items: [
    {
      label: __("New Account"),
      action: () => {
        frappe.new_doc("Account", true);
      },
      condition: 'frappe.boot.user.can_create.indexOf("Account") !== -1',
    },
  ],
  onload: (treeview) => {
    treeview.make_tree();
  },
};
