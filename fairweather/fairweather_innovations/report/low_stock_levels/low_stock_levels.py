# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cstr

__all__ = ["execute"]

def execute(filters={}):
	return get_columns(filters), \
		get_data(filters)

def get_conditions(filters):
	"""
	Return sql conditions ready to use in query
	"""
	conditions = (
		("Bin", "item_code", "=", "%(item_code)s"),
		("Bin", "warehouse", "=", "%(warehouse)s"),
		("Item", "safety_stock", ">=", "`tabBin`.`actual_qty`"),
		("Item", "item_group", "=", "%(item_group)s"),
		# ("Item", "disabled", "=", 0),
	)

	sql_conditions = list()

	for doctype, fieldname, compare, value in conditions:
		if fieldname in filters:
			sql_condition = "`tab{doctype}`.`{fieldname}` {compare} {value}" \
				.format(doctype=doctype, fieldname=fieldname, compare=compare,
					value=value)

			sql_conditions.append(sql_condition)

	return " And ".join(sql_conditions)

def get_formatted_field(label, width=100, fieldtype=None):
	"""
	Returns formatted string
		[Label]:[Field Type]/[Options]:[Width]
	"""
	from frappe import _

	parts = (
		_(label).title(),
		fieldtype if fieldtype else "Data",
		cstr(width),
	)
	return ":".join(parts)

def get_data(filters):
	"""
	Return the data that needs to be rendered
	"""
	fields = get_fields(filters)
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		Select
			{fields}
		From
			`tabBin`
		Inner Join
			`tabItem`
			On
				`tabBin`.item_code = `tabItem`.item_code
		Where
			`tabItem`.disabled = 0
			And {conditions}
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, debug=False)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""

	columns = (
		("Item Code", "item_code", "Link/Item"),
		("Description", "description", "Data"),
		("Item Group", "item_group", "Link/Item Group"),
		("Default Supplier", "default_supplier", "Link/Supplier"),
		("Stock Uom", "stock_uom", "Link/UOM"),
		("Actual Qty", "actual_qty", "Float"),
		("Safety Stock", "safety_stock", "Float"),
		("Minimum Order Qty", "min_order_qty", "Float"),
		("Valuation Rate", "valuation_rate", "Currency"),
		("Projected Qty", "projected_qty", "Float"),
		("Reserved Qty For Production", "reserved_qty_for_production", "Float"),
		("Reserved Qty", "reserved_qty", "Float"),
		# ("Planned Qty", "planned_qty", "Float"),
		# ("Indented Qty", "indented_qty", "Float"),
		("Warehouse", "warehouse", "Link/Warehouse"),
		("Ordered Qty", "ordered_qty", "Float"),
		# ("Reserved Qty For Sub Contract", "reserved_qty_for_sub_contract", "Float"),
		("Stock Value", "stock_value", "Currency"),
	)

	formatted_columns = list()

	for label, fieldname, fieldtype in columns:
		formatted_column = get_formatted_field(label=label,
			fieldtype=fieldtype)

		formatted_columns.append(formatted_column)

	return formatted_columns

def get_fields(filters):
	"""
	Return sql fields ready to be used on query
	"""

	fields = (
		("Bin", "item_code"),
		("Item", "description"),
		("Item", "item_group"),
		("Item", "default_supplier"),
		("Bin", "stock_uom"),
		("Bin", "actual_qty"),
		("Item", "safety_stock"),
		("Item", "min_order_qty"),
		("Bin", "valuation_rate"),
		("Bin", "projected_qty"),
		("Bin", "reserved_qty_for_production"),
		("Bin", "reserved_qty"),
		# ("Bin", "planned_qty"),
		# ("Bin", "indented_qty"),
		("Bin", "warehouse"),
		("Bin", "ordered_qty"),
		# ("Bin", "reserved_qty_for_sub_contract"),
		("Bin", "stock_value"),
	)

	sql_fields = list()

	for doctype, fieldname in fields:
		sql_field = "`tab{doctype}`.`{fieldname}`" \
			.format(doctype=doctype, fieldname=fieldname)

		sql_fields.append(sql_field)

	return ", ".join(sql_fields)
