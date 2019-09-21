// Copyright (c) 2018, Yefri Tavarez and contributors
// For license information, please see license.txt

frappe.ui.form.on('Local Tax Rates', {
	"onload_post_render": function(frm) {
		// set docstatus equals one to make the form read only
		frm.doc.docstatus = 1;
		frm.refresh();

		frm.add_custom_button(__("Edit"), function() {
			frm.trigger("make_editable");
		});
	},
	"make_editable": function(frm) {
		frm.doc.docstatus = 0;

		frm.refresh();
	}
});
