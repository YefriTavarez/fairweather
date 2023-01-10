// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

frappe.ui.form.on("Item", {
	onload_post_render(frm) {
		if (frm.is_new()) {
			frm.trigger("set_custom_opts");
		}
	},
	set_custom_opts(frm) {
		const { doc } = frm;

		if (doc.item_code && !doc.item_name) {
			// then it must be a duplicate

			const { events } = frm;

			const olddoc = frappe.get_doc(doc.doctype, doc.item_code);

			events._update_custom_opts(doc);
			events._self_update_with_original(frm, olddoc, doc);
		}
	},
	_update_custom_opts(doc) {
		const { item_code } = doc;
		const { stringify, parse } = JSON;

		let custom_opts = "{}";

		try {
			custom_opts = parse(doc.custom_opts);
		} catch (error) {
			// pass
		}

		Object.assign(custom_opts, {
			item_code,
		});

		doc.custom_opts = stringify(custom_opts);
	},
	_self_update_with_original(frm, olddoc, newdoc) {
		newdoc.description = olddoc.description;
		newdoc.item_name = olddoc.item_name;

		frm.refresh_fields();
	}
});