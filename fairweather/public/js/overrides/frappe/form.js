(function () {
	const { prototype } = frappe.ui.form.Form;

	console.log("hey from form override");

	prototype.execute_action = function (action) {
		if (typeof action === "string") {
			// called by label - maybe via custom script
			// frm.execute_action('Action')
			for (let _action of this.meta.actions) {
				if (_action.label === action) {
					action = _action;
					break;
				}
			}

			if (typeof action === "string") {
				frappe.throw(`Action ${action} not found`);
			}
		}
		if (action.action_type === "Server Action") {
			return frappe.xcall(action.action, { doc: this.doc }).then((doc) => {
				if (doc.doctype) {
					// document is returned by the method,
					// apply the changes locally and refresh
					frappe.model.sync(doc);
					this.refresh();
				}

				// feedback
				frappe.msgprint({
					message: __("{} Complete", [action.label]),
					alert: true,
				});
			});
		} else if (action.action_type === "Route") {
			return frappe.set_route(action.action);
		}
	}
})();