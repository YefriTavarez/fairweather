// Copyright (c) 2021, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales by Item"] = {
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		if (cell === 3) {
			const docfield = {
				fieldtype: "Float",
				precision: 0,
				bold: true,
			};

			return frappe.format(value, docfield);
		}

		return default_formatter(row, cell, value, columnDef, dataContext);
	},

	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
		},
	]
}
