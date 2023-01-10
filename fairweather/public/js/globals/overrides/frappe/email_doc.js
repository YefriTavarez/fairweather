// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

(function () {
	const { prototype } = frappe.ui.form.Form;

	prototype.email_doc = function (message) {
		const { doc } = this;

		if (typeof message === "string") {
			message = { message };
		}

		if (!message) {
			message = "";

			if (doc.customer) {
				message += frappe.dedent(`
					<p>
						Dear <i>${doc.customer_name || doc.customer}</i>.
					</p>
					<br>`);
			}

			let type = "document";
			if (doc.doctype === "Sales Order") {
				type = "order"
			} else if (doc.doctype === "Sales Invoice") {
				type = "invoice"
			} else if (doc.doctype === "Sales Invoice") {
				type = "delivery receipt"
			} else {
				if (doc.doctype) {
					type = doc.doctype;
				}
			}

			message += `Thank you for your order. Your ${type} is attached.
				<br>Please let me know if you have any questions or if you need anything further.
				<br>
				<br>Thanks again!`;
		}

		const doctypes_with_contact = [
			"Sales Order",
			"Sales Invoice",
			"Sales Invoice",
		];

		if (doctypes_with_contact.includes(doc.doctype)) {
			return frappe.db
				.get_value("Contact", doc.contact_person, "email_id")
				.then(({ message }) => {
					if (message) {
						return message.email_id;
					}
				})
				.then(email => {
					const real_name = doc.real_name
						|| doc.contact_display
						|| doc.contact_name;

					new frappe.views.CommunicationComposer({
						doc: doc,
						frm: this,
						subject: "Seaview " + __(this.meta.name) + ": " + this.docname,
						recipients: email || "",
						attach_document_print: true,
						message: message,
						real_name: real_name
					});
				});
		}

		return new frappe.views.CommunicationComposer({
			doc: this.doc,
			frm: this,
			subject: `Seaview ${__(this.meta.name)}: ${this.docname}`,
			recipients: doc.email || doc.email_id || doc.contact_email,
			attach_document_print: true,
			message: message,
		});
	};
})();