frappe.ui.form.on("Delivery Note", {
	"onload": function(frm) {
		frm.add_fetch("location", "local_rate", "local_rate");
		frm.add_fetch("customer", "customer_type", "customer_type");
	},
	"refresh": function(frm) {
		frm.trigger("customer_type");
	},
	"customer_type": function(frm) {
		// frm.toggle_reqd("location", frm.doc.customer_type == "Individual");
	},
	"location": function(frm) {
		frm.doc.taxes_and_charges = "State and Local Taxes - SV";
		frm.trigger("taxes_and_charges")
			.then(({ message }) => { 
				var row = frm.events.get_row_based_on_account(frm);
			
				row.description = frm.doc.location;
				row.rate = frm.doc.local_rate;
				
				frm.cscript.calculate_taxes_and_totals(true);
			});

	},
	"get_row_based_on_account": function(frm) {
		var row = null;

		$.map(frm.doc.taxes, function(d) {
			if (d.account_head == "2320 - Local Taxes - SV") {
				row = d;
			}
		});

		return row;
	},
});