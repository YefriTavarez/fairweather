(function () {
	const { prototype } = frappe.ui.form.PrintView;
	const { make } = prototype;

	prototype.make = function () {
		make.call(this); // run the original

		// finally run my custom code
		add_custom_actions.call(this);
	}

	const add_custom_actions = function () {
		this.page.add_action_icon(
			"mail",
			() => {
				show_send_email_dialog.call(this);
			},
			"",
			__("Email")
		);
	};

	const show_send_email_dialog = function () {
		let { frm } = this;

		if (!frm.get_files) {
			frappe.model.with_doctype(frm.doctype, _ => {
				frappe.model.with_doc(frm.doctype, frm.docname, _ => {
					const doc = frappe.get_doc(frm.doctype, frm.docname);

					frm = new frappe.ui.form.Form(frm.doctype, self.page, false, null);

					frm.doctype = doc.doctype;
					frm.docname = doc.name;
					Object.assign(frm, { doc });
				}).finally(_ => {
					const attachments = {
						get_attachments() {
							const { attachments } = frm.get_docinfo();
							return attachments;
						},
					};

					Object.assign(frm, { attachments });
					frm.email_doc();
				});
			})
		} else {
			frm.email_doc();
		}
	}
})();