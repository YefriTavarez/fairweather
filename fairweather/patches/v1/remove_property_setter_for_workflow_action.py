# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe


def execute():
    doctype = "Property Setter"
    name = "Workflow Action-main-autoname"

    try:
        frappe.delete_doc_if_exists(doctype, name)
    except:  # pylint: disable=bare-except
        print(f"Failed to delete {doctype} {name}")
