// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

frappe.ui.form.on("Sales Order", {
	onload(frm) {
		frm.add_fetch("customer", "customer_type", "customer_type");
	},
	refresh(frm) {
		frappe.run_serially([
			_ => frm.trigger("set_queries"),
			_ => frm.trigger("add_custom_buttons"),
		]);
	},
	on_submit(frm) {
		frm.email_doc();
	},
	set_queries(frm) {
		const fieldname = "avalara_tax_rate";
		const query = _ => {
			const { doc } = frm;
			const filters = {
				"state": doc.avalara_state,
			};

			return { filters };
		};

		frm.set_query(fieldname, query);
	},
	add_custom_buttons(frm) {
		const { doc } = frm;

		if (doc.docstatus === 1 && doc.customer) {
			const label = __("Email");
			const fancy_label = __("Email <i>{0}</i>", [doc.customer_name || doc.customer]);
			const action = _ => frm.email_doc();

			const email_btn = frm.add_custom_button(label, action);
			email_btn.html(fancy_label);
		}
	},
	avalara_tax_rate(frm) {
		const { doc } = frm;

		if (!doc.avalara_tax_rate) {
			return "No value for Avalara Tax Rate: Skipping.";
		}

		if (frm.avalara_tax_rate && frm.avalara_tax_rate === doc.avalara_tax_rate) {
			return "Avalara Tax Rate unchanged: Skipping.";
		} else {
			frm.avalara_tax_rate = doc.avalara_tax_rate;
		}

		const method = "fairweather.api.add_taxes_if_needed";
		const args = { doc };

		doc.taxes_and_charges = null;

		frappe.call({ method, args })
			.then(({ message: docs }) => {
				if (jQuery.isPlainObject(docs)) {
					frappe.run_serially([
						_ => frappe.model.sync([docs]),
						_ => frm.refresh_fields(),
						_ => frappe.toast({
							indicator: "green",
							message: __("Tax table has been updated"),
						}),
					]);
				}
			});
	},
	set_delivery_date(frm) {
		const { doc } = frm;
		const parentfield = "items";

		for (const item of doc[parentfield]) {
			item.delivery_date = doc.delivery_date;
		}

		frm.refresh_field(parentfield);
	},
});