import frappe

def validate(doc, method):
	email_id = doc.get("email_id")

	if not email_id:
		return

	customers = [d.link_name
		for d in doc.links
		if d.link_doctype == "Customer"]

	# frappe.errprint(customers)

	for doctype in (
		"Sales Invoice",
		"Sales Order",
		"Delivery Note",
		"Quotation"
	):
		doclist = frappe.get_all(doctype, {
			"customer": ("in", customers),
		}, ["name"])

		for dname in doclist:
			frappe.db \
				.set_value(doctype,
					dname.name,
					"contact_email",
					email_id,
					update_modified=False)
