// Copyright (c) 2016, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplies in Sales Orders"] = {
    "filters": [
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": __("Company"),
            "options": "Company",
            "reqd": 1,
            "default": frappe.sys_defaults.company,
        },
        {
            "fieldname": "from_date",
            "fieldtype": "Date",
            "label": __("From Date"),
            "default": frappe.datetime.month_start(),
        },
        {
            "fieldname": "to_date",
            "fieldtype": "Date",
            "label": __("To Date"),
            "default": frappe.datetime.month_end(),
        },
        {
            "fieldname": "supply_item",
            "fieldtype": "Link",
            "options": "Item",
            "label": __("Supply Item"),
            "reqd": 1,
            "get_query": {
                "filters": {
                    "is_purchase_item": 1
                }
            }
        },
        {
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "label": __("Customer"),
        },
        {
            "fieldname": "bom",
            "fieldtype": "Link",
            "options": "BOM",
            "label": __("BOM"),
        },
        {
            "fieldname": "include_draft_orders",
            "fieldtype": "Check",
            "default": 0,
            "label": __("Include Draft Orders?")
        },
    ]
}
