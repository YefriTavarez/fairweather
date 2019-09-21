# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

import unittest

class TestLowStockLevels(unittest.TestCase):
	def runTest(self):
		self.test_get_formatted_field()
		self.test_get_conditions()
		self.test_get_fields()
		self.test_get_columns()

	def test_get_conditions(self):
		from .low_stock_levels import get_conditions

		filters = {
			"warehouse": None,
		}

		expected_result = "`tabBin`.`warehouse` = %(warehouse)s"

		result = get_conditions(filters)

		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(expected_result, result)

		filters = {
			"item_code": None,
			"warehouse": None,
		}

		expected_result = "`tabBin`.`item_code` = %(item_code)s" \
			" And `tabBin`.`warehouse` = %(warehouse)s"

		result = get_conditions(filters)

		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(expected_result, result)

	def test_get_formatted_field(self):
		from .low_stock_levels import get_formatted_field

		expected_result = "Employee:Link/Employee:200"
		result = get_formatted_field(label="Employee", fieldtype="Link/Employee", width=200)
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Employee:Data:100"
		result = get_formatted_field(label="Employee", fieldtype="Data", width="100")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Employee:Data:200"
		result = get_formatted_field(label="Employee", fieldtype="Data", width="200")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Employee:Data:100"
		result = get_formatted_field(label="Employee", fieldtype="Data")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Rate:Currency:120"
		result = get_formatted_field(label="Rate", fieldtype="Currency", width="120")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Rate:Data:120"
		result = get_formatted_field(label="Rate", width=120)
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Rate:Data:120"
		result = get_formatted_field(label="Rate", fieldtype="Data", width="120")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

		expected_result = "Rate:Data:100"
		result = get_formatted_field(label="Rate", fieldtype="Data")
		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)

	def test_get_columns(self):

		from .low_stock_levels import get_columns

		expected_results = [
			u'Item Code:Link/Item:100',
			u'Item Name:Data:100',
			u'Stock Uom:Link/UOM:100',
			u'Actual Qty:Float:100',
			u'Safety Stock:Float:100',
			u'Valuation Rate:Currency:100',
			u'Projected Qty:Float:100',
			u'Reserved Qty For Production:Float:100',
			u'Reserved Qty:Float:100',
			u'Planned Qty:Float:100',
			u'Indented Qty:Float:100',
			u'Warehouse:Link/Warehouse:100',
			u'Ordered Qty:Float:100',
			u'Reserved Qty For Sub Contract:Float:100',
			u'Stock Value:Currency:100'
		]

		results = get_columns({})

		for column in results:
			if column in expected_results:
				continue

			frappe.throw("Unexpected column {}".format(column))

		for column in expected_results:
			if column in results:
				continue

			frappe.throw("Missing column {}".format(column))

	def test_get_fields(self):

		from .low_stock_levels import get_fields

		expected_result = u'`tabBin`.`item_code`, `tabItem`.`item_name`, ' \
			'`tabBin`.`stock_uom`, `tabBin`.`actual_qty`, `tabItem`.`safety_stock`, ' \
			'`tabBin`.`valuation_rate`, `tabBin`.`projected_qty`, ' \
			'`tabBin`.`reserved_qty_for_production`, `tabBin`.`reserved_qty`, ' \
			'`tabBin`.`planned_qty`, `tabBin`.`indented_qty`, `tabBin`.`warehouse`, ' \
			'`tabBin`.`ordered_qty`, `tabBin`.`reserved_qty_for_sub_contract`, ' \
			'`tabBin`.`stock_value`'

		result = get_fields({})

		print("exp: {} found: {}".format(expected_result, result))

		self.assertEqual(result, expected_result)


