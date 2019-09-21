frappe.ui.form.on("Sales Invoice", {
	onload: frm => {
		$.each({
			location: "local_rate",
			customer: "customer_type"
		}, (link, value) => {
			frm.add_fetch(link, value, value);
		});
	},
	refresh: frm => {
		$.map([
			"customer_type",
			"add_fetches",
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
					subject: "Seaview "+ __(frm.meta.name) + ": " + frm.docname,
					recipients: email || "",
					attach_document_print: true,
					message: sales_invoice_message,
					real_name: real_name
				});
			});
	},
	location: frm => {
		frm.doc.taxes_and_charges = "State and Local Taxes - SV";
		frm.trigger("taxes_and_charges")
			.then(({ message }) => {
				let row = frm.events.get_row_based_on_account(frm);

				row.description = frm.doc.location;
				row.rate = frm.doc.local_rate;

				frm.cscript.calculate_taxes_and_totals(true);
			});
	},
	get_row_based_on_account: frm => {
		let row = null;

		$.map(frm.doc.taxes, function(d) {
			if (d.account_head === "2320 - Local Taxes - SV") {
				row = d;
			}
		});

		return row;
	}
});
