// Copyright (c) 2016, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

(function () {
    frappe.query_reports["Contact Report"] = {
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
                fieldname: "contact_role",
                fieldtype: "Link",
                label: "Contact Role",
                options: "Contact Role",
                get_query: {
                    filters: {
                        enabled: true,
                    }
                }
            },
        ]
    };
})();