// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt

{
	// form events
	function refresh(frm) {
		set_queries(frm)
		add_secondary_action(frm)
	}

	function customer_and_email_add(frm, doctype, name) {
		frm.refresh()
		set_search_on_custom_added_row(frm, doctype, name)
	}
	
	function customer_and_email_remove(frm) {
		frappe.run_serially([
			_ => frm.refresh(),
			_ => uncheck_allow_multiple_fetches_if_empty_table(frm),
		])
	}

	// fields and buttons events
	function fetch_customers(frm) {
		if (!validate_filters(frm, false)) {
			confirm_on_empty_filters(frm)
		} else {
			do_fetch_customers(frm)
		}
	}

	function remove_customers_without_email(frm) {
		frappe.dom.freeze("Removing Customers without an Email")
		frm.call("remove_customers_without_email")
			.then(_ => {
				frappe.show_alert({
					"message": __("Customers without an Email have been removed"),
					"indicator": "green"
				})
			}, _ => {
				frappe.show_alert({
					"message": __("Oops! Something went wrong while removing customers without an Email"),
					"indicator": "red"
				})
			}).always(_ => {
				frappe.dom.unfreeze()
				frm.dirty()
			})
	}

	function email(frm) {
		frm.refresh()
	}

	// other events
	function set_queries(frm) {
		set_receivable_account_query(frm)
	}

	function add_secondary_action(frm) {
		frm.page.set_secondary_action("Reload", async function(event) {
			frm.reload_doc()

			frappe.show_alert({
				"message": __("Form has been reloaded from the server"),
				"indicator": "green"
			})
		}, null, "Reloading")
		.attr("title", "Reload the Form from the Server") // add tooltip text
			.attr("data-toggle", "tooltip") // enable tooltip
			.attr("data-placement", "bottom") // place the tooltip on top of the item
			.tooltip() // initialize tooltip
	}

	function set_receivable_account_query(frm) {
		const { doc } = frm

		const fieldname = "account"
		function get_query() {
			const filters = {
				"account_type": "Receivable",
			}

			return { filters }
		}

		frm.set_query(fieldname, get_query)
	}

	function uncheck_allow_multiple_fetches_if_empty_table(frm) {
		const { doc } = frm

		if (doc.allow_multiple_fetches && !doc.customer_and_email?.length) {
			frm.set_value("allow_multiple_fetches",  false)
		}
	}

	function set_search_on_custom_added_row(frm, doctype, name) {
		const { model } = frappe
		const fieldname = "search"
		const value = "Added Manually"

		model.set_value(doctype, name, fieldname, value)
	}

	function validate_filters(frm, raise) {
		if (!raise) {
			raise = false
		}

		const filters = [
			"price_list",
			"customer_group",
			"payment_terms",
			"account",
		]
		
		for (const fieldname of filters) {
			if (frm.doc[fieldname]) {
				return true
			}
		}

		if (raise) {
			frappe.throw(__("Please set at least one filter"))
		}

		return false
	}

	function confirm_on_empty_filters(frm) {
		const message = `
			No filters have been set. It can slow or even crash your browser 
			if there are too many results. Do you want to continue?
		`
		function ifyes() { 
			do_fetch_customers(frm)
		}

		function ifno() { 
			frappe.show_alert({
				"message": "Nothing changes made",
				"indicator": "blue"
			})
		}

		frappe.confirm(message, ifyes, ifno)
	}

	function do_fetch_customers(frm) {
		frappe.dom.freeze("Fetching Customers")
		frm.call("fetch_customers")
			.then(_ => {
				frappe.show_alert({
					"message": __("Customers table has been updated"),
					"indicator": "green"
				})
			}, _ => {
				frappe.show_alert({
					"message": __("Oops! Something went wrong while fetching customers"),
					"indicator": "red"
				})
			}).always(_ => {
				frappe.dom.unfreeze()
				frm.dirty()
			})
	}


	// main form
	frappe.ui.form.on("Monthly Statement Configurator", {
		refresh,
		fetch_customers,
		remove_customers_without_email,
	})

	// child table
	frappe.ui.form.on("Customer and Email", {
		customer_and_email_add,
		customer_and_email_remove,
		email, // form field
	})
}
