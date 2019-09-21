import frappe

def get_unique_list_of(key, map):
	unique_keys = []

	for d in map:
		if not d[key] in unique_keys:
			unique_keys.append(d[key])

	return unique_keys

def cancel_stock_entries():
	stock_reconciliation_map = frappe.db.sql("""
		select 
			child.item_code, 
			child.parent as name,
			child.docstatus,
			parent.posting_time, 
			parent.posting_date 
		from `tabStock Reconciliation Item` as child
		inner join `tabStock Reconciliation` as parent
			on child.parent = parent.name
		where 1 = 1""", as_dict=True)
	

def cancel_docs_map(doctype, map, key="name"):
	for each in get_unique_list_of(key, map):
		if each.docstatus == 1:
			cancel_doc(doctype, each.get(key))

def cancel_doc(doctype, docname):
	doc = frappe.get_doc(doctype, docname)

	if doc.docstatus == 1:
		doc.cancel()
