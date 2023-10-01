# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe


def get_context(context):
    additional_context = {
        "whitelisted_customers": get_whitelist_customers(),
    }

    return additional_context


def get_whitelist_customers(date=None):
    doctype = "Mute Email Notifications for Customer"
    filters = {
        # "enabled": 1,
    }

    pluck = "customer"

    return frappe.get_all(doctype, filters=filters, pluck=pluck)
