frappe.ui.form.on("Sales Invoice", {
	refresh: frm => {
		jQuery.map([
			"customer_type",
			"add_fetches",
			"set_queries",
			"add_custom_buttons",
		], event => frm.trigger(event));
	},
	onload_post_render: frm => {
		frm.trigger("toggle_enabled_on_submitted_fields");
	},
	validate: frm => {
		const { doc } = frm,
			{ db } = frappe,
			{ get_value } = db;

		if (doc.outstanding_amount > 0.000 && !doc.tc_name) {
			frappe.validated = false;

			doc.tc_name = "Sales Terms and Conditions";
			get_value("Terms and Conditions", doc.tc_name, "terms")
				.then(({ message }) => {

					frappe.validated = true;
					doc.terms = message.terms;

					frm.save();
				});
		}
	},
	add_fetches: frm => {
		frm.add_fetch("customer", "discount_terms_template",
			"discount_terms_template");
	},
	set_queries: frm => {
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
	toggle_enabled_on_submitted_fields: frm => {
		let enable = [
			"Overdue",
			"Draft",
			"Unpaid"
		].includes(frm.doc.status);

		frm.toggle_enable([
			"po_no",
			"po_date",
			"shipping_method",
			"tracking_number"
		], enable);
	},
	add_custom_buttons: frm => {
		if (frm.doc.docstatus === 1 && frm.doc.contact_person) {
			frm.add_custom_button(__("Email"), event => frm.trigger("send_email"));
		}
	},
	send_email: frm => {
		const { sales_invoice_message } = frappe.boot.notification_settings;

		frappe.db
			.get_value("Contact", frm.doc.contact_person, "email_id")
			.then(({ message }) => {
				if (message) {
					return message.email_id;
				}
			})
			.then(email => {
				const real_name = frm.doc.real_name
					|| frm.doc.contact_display
					|| frm.doc.contact_name;

				new frappe.views.CommunicationComposer({
					doc: frm.doc,
					frm: frm,
					subject: "Seaview " + __(frm.meta.name) + ": " + frm.docname,
					recipients: email || "",
					attach_document_print: true,
					message: sales_invoice_message,
					real_name: real_name
				});
			});
	},
	avalara_tax_rate: frm => {
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
});
