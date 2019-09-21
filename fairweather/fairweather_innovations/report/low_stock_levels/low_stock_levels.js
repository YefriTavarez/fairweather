// Copyright (c) 2016, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

(function() {
	const {
		boot,
	} = frappe,
	{ sysdefaults } = boot,
	{ default_warehouse } = sysdefaults;

	frappe.query_reports["Low Stock Levels"] = {
		"filters": [
			{
				fieldname: "item_group",
				fieldtype: "Link",
				label: __("Item Group"),
				options: "Item Group",
				get_query: event => {
					return {
						filters: {
							is_group: 0,
						}
					}
				},
				on_change: event => {
					const { query_report_filters_by_name, } = frappe,
						{ item_code = {}} = query_report_filters_by_name;

					item_code.set_value(undefined);
				}
			},
			{
				fieldname: "item_code",
				fieldtype: "Link",
				options: "Item",
				label: __("Item Code"),
				reqd: false,
				get_query: event => {
					const { query_report_filters_by_name, } = frappe,
						{ item_group = {}} = query_report_filters_by_name,
						item_group_value = item_group.get_value();

					if ( ! "get_value" in item_group) {
						item_group = function() {
							return undefined;
						}
					}

					let filters = {
						disabled: 0,
					};

					if (item_group_value) {
						filters["item_group"] = item_group_value;
					}

					return { filters };
				}
			},
			{
				fieldname: "warehouse",
				fieldtype: "Link",
				options: "Warehouse",
				label: __("Warehouse"),
				default: default_warehouse,
				reqd: true,
			},
			{
				fieldname: "safety_stock",
				fieldtype: "Check",
				label: __("Show Only Low Levels"),
				default: true,
			},
		]
	}
})();
