// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

frappe.render_grid = function (opts) {
	// build context
	if (opts.grid) {
		opts.columns = opts.grid.getColumns();
		opts.data = opts.grid.getData().getItems();
	}

	if (
		opts.print_settings &&
		opts.print_settings.orientation &&
		opts.print_settings.orientation.toLowerCase() === "landscape"
	) {
		opts.landscape = true;
	}

	// show landscape view if columns more than 10
	if (opts.landscape == null) {
		if (opts.columns && opts.columns.length > 10) {
			opts.landscape = true;
		} else {
			opts.landscape = false;
		}
	}

	// render content
	if (!opts.content) {
		opts.content = frappe.render_template(opts.template || "print_grid", opts);
	}

	// render HTML wrapper page
	opts.base_url = frappe.urllib.get_base_url();
	opts.print_css = frappe.boot.print_css;

	(opts.lang = opts.lang || frappe.boot.lang),
		(opts.layout_direction = opts.layout_direction || frappe.utils.is_rtl() ? "rtl" : "ltr");

	var html = frappe.render_template("print_template", opts);

	var w = window.open();

	if (cur_frm && cur_frm.doctype == "Customer") {
		frappe.run_serially([
			_ => frappe.timeout(1.5),
			_ => {
				w.print();
			},
		])
	}

	if (!w) {
		frappe.msgprint(__("Please enable pop-ups in your browser"));
	}

	w.document.write(html);
	w.document.close();
};