(function () {
	const { prototype } = frappe.ui.form.Form;

	prototype.email_doc = function (message) {
		if (!message) {
			const { doc } = this;
			console.log({ self: this });
			if (doc.customer) {
				message = `Dear ${doc.customer_name || doc.customer}.<br>`;
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

			message += `
				<br>Thank you for your order. Your ${type} is attached.
				<br>Please let me know if you have any questions or if you need anything further.
				<br>
				<br>Thanks again!`;
		}

		return new frappe.views.CommunicationComposer({
			doc: this.doc,
			frm: this,
			subject: __(this.meta.name) + ": " + this.docname,
			recipients: this.doc.email || this.doc.email_id || this.doc.contact_email,
			attach_document_print: true,
			message: message,
		});
	};
})();