// Copyright (c) 2022, Yefri Tavarez and contributors
// For license information, please see license.txt

frappe.ui.form.on("Avalara Tax Rate", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.disable_form();
		}
	}
});
