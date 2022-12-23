frappe.ui.form.on("Delivery Note", {
	"onload": function (frm) {
		frm.add_fetch("customer", "customer_type", "customer_type");
	},
	"refresh": function (frm) {
		frm.trigger("set_queries");
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
				frappe.run_serially([
					_ => frappe.model.sync([docs]),
					_ => frm.refresh_fields(),
					_ => frappe.toast({
						indicator: "green",
						message: __("Tax table has been updated"),
					}),
				]);
			});
	},
});