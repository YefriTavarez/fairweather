class PrintView extends frappe.ui.form.PrintView {
	constructor(wrapper) {
		super(wrapper);

		this.add_custom_actions();
	}

	add_custom_actions() {
		this.page.add_action_icon(
			"mail",
			() => {
				this.show_send_email_dialog();
			},
			"",
			__("Email")
		);
	}

	show_send_email_dialog() {
		const { frm } = this;
		const { doc } = frm;

		this.doc = doc;

		this.frm.perm = [{ email: 1 }];
		if (!jQuery.isFunction(this.frm.get_files)) {
			this.frm.get_files = _ => [];

			frappe.show_alert({
				message: `It looks like this page no longer has the Attachments.
				If you need to send any of the attachments, please go back
				to the document and without reloading the try to email again.
				`,
				indicator: "yellow",
			});
		}

		const inform_of_status = _ => {
			frappe.show_alert({
				message: `Email Sent`,
				indicator: "green",
			});
		};

		let about_to_send = true;
		let sent_email = false;
		if (!jQuery.isFunction(this.frm.reload_doc)) {
			this.frm.reload_doc = inform_of_status;
		} else { // if it's set, then override
			const self = this;
			this.frm.reload_doc = _ => {
				if (!sent_email && about_to_send) {
					inform_of_status();
					sent_email = true;
				}

				self.frm.check_doctype_conflict(self.frm.docname);

				if (!self.frm.doc.__islocal) {
					frappe.model.remove_from_locals(self.frm.doctype, self.frm.docname);
					return frappe.model.with_doc(self.frm.doctype, self.frm.docname, () => {
						self.frm.refresh();
					});
				}
			};
		}

		let message = ``;
		new frappe.views.CommunicationComposer({
			doc: doc,
			frm: this.frm,
			subject: __(doc.title) + ": " + doc.name,
			recipients: doc.email || doc.email_id || doc.contact_email,
			// attach_document_print: true,
			message: message,
		});
	}
};

frappe.ui.form.PrintView = PrintView;