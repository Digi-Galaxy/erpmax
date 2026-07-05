frappe.treeview_settings["Item Category"] = {
	ignore_fields: ["parent_item_category"],
	get_tree_nodes: "erpmax.inventory.doctype.item_category.item_category.get_children",
	add_tree_node: "erpmax.inventory.doctype.item_category.item_category.add_node",
	filters: [
		{
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			label: __("Company"),
			get_query: () => ({
				filters: [["Company", "is_group", "=", 0]],
			}),
		},
	],
	breadcrumb: "Inventory",
	root_label: "All Item Categories",
	get_tree_root: false,
	menu_items: [
		{
			label: __("New Item Category"),
			action: function () {
				frappe.new_doc("Item Category", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Item Category") !== -1',
		},
	],
	onload: function (treeview) {
		treeview.make_tree();
	},
};
