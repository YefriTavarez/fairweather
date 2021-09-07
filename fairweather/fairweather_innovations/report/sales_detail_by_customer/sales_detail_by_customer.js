// Copyright (c) 2016, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

(function ({ datetime }) {
	const repname = "Sales Detail by Customer";
	const SalesDetailByCustomer = {
		"filters": [
			{
				"fieldtype": "Link",
				"fieldname": "customer",
				"label": __("Customer"),
				"options": "Customer",
				"reqd": true,
			},
			{
				"fieldtype": "Date",
				"fieldname": "from_date",
				"label": __("From Date"),
			},
			{
				"fieldtype": "Date",
				"fieldname": "to_date",
				"label": __("To Date"),
			},
		],
	};

	frappe.query_reports[repname] = SalesDetailByCustomer;
})(frappe);
