// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ordered Items To Be Delivered"] = {
	"filters": [
		{
			label: "Company",
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.sys_defaults.company,
		},
		
		{
			label: "From Date",
			fieldname: "from_date",
			fieldtype: "Date",
		},
		
		{
			label: "To Date",
			fieldname: "to_date",
			fieldtype: "Date",
		},

		{
			label: "Customer",
			fieldname: "customer",
			fieldtype: "Link",
			options: "Customer",
		},

		{
			label: "Item",
			fieldname: "item",
			fieldtype: "Link",
			options: "Item",
		},

		{
			label: "Item Group",
			fieldname: "item_group",
			fieldtype: "Link",
			options: "Item Group",
		},

		{
			label: "Warehouse",
			fieldname: "warehouse",
			fieldtype: "Link",
			options: "Warehouse",
		},

		{
			label: "Shipping Method",
			fieldname: "shipping_method",
			fieldtype: "Data",
		},
	]
};
