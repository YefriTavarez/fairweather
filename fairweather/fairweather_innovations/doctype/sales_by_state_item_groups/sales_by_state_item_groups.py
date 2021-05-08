# -*- coding: utf-8 -*-
# Copyright (c) 2021, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesbyStateItemGroups(Document):
	pass

def get_sales_by_state_items_groups():
	item_group_list = frappe.get_list("Sales by State Item Groups", {
		"parentfield": "sales_by_state_item_groups",
		"parenttype": "Selling Settings",
		"parent": "Selling Settings",
	}, ["item_group"])

	# as list true
	return [d.item_group for d in item_group_list]
