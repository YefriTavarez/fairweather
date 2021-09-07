import json
import frappe

def after_insert(doc, method):
	if doc.custom_opts == "{}":
		return "not a duplicated item"

	custom_opts = None

	try:
		custom_opts = json.loads(doc.custom_opts)
	except:
		pass

	if not custom_opts:
		return "invalid json format"

	if not custom_opts["item_code"]:
		return "not item_code sent"

	create_item_prices(custom_opts["item_code"], doc)

def create_item_prices(item_code, newdoc):
	doctype = "Item Price"

	filters = {
		"item_code": item_code,
	}

	doclist = frappe.get_all(doctype, filters, as_list=True)

	for name, in doclist:
		doc = frappe.get_doc(doctype, name)

		item_price = frappe.copy_doc(doc)

		# change to the new item_code
		item_price.item_code = newdoc.item_code

		item_price.save(ignore_permissions=True)
