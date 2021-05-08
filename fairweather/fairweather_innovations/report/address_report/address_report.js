// Copyright (c) 2021, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

(function () {
	frappe.query_reports["Address Report"] = {
		"filters": [
			{
				fieldname: "customer_group",
				fieldtype: "Link",
				label: "Customer Group",
				options: "Customer Group",
				get_query: {
					filters: {
						is_group: false,
					}
				}
			},
			{
				fieldname: "customer_type",
				fieldtype: "Select",
				label: "Customer Type",
				options: "\nCompany\nIndividual",
			},
			{
				fieldname: "account",
				fieldtype: "Link",
				label: "Account",
				options: "Account",
				get_query: {
					filters: {
						account_type: "Receivable",
					}
				}
			},
		]
	};
})();