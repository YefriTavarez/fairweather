// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt

{
	function refresh(frm) {

	}

	function customer(frm) {
		const { doc } = frm
		
		if (!doc.customer) {
			return "Skip for empty customer"
		}

		fetch_statement_of_accounts(frm)
	}

	function as_of_date(frm) {
		const { doc } = frm
		
		if (!doc.as_of_date) {
			return "Skip for empty date"
		}

		fetch_statement_of_accounts(frm)
	}

	function fetch_statement_of_accounts(frm) {
		const { doc } = frm
		
		if (!doc.customer) {
			return "Skip for empty customer"
		}
		
		if (!doc.as_of_date) {
			return "Skip for empty date"
		}

		// to prevent duplicated calls at the same time
		// for some unknown reasons the framework is calling
		// the field handlers twice or something like that
		if (frm._fetching_statement_of_accounts) {
			return "Skip for duplicated calls"
		}

		frm._fetching_statement_of_accounts = true

		frappe.dom.freeze("Fetching Statement of Accounts")

		frm.call("fetch_statement_of_accounts")
			.then(_ => {
				frappe.show_alert({
					"message": __("Statement of Accounts has been fetched"),
					"indicator": "green"
				})

				frm.refresh()
			}, _ => {
				frappe.show_alert({
					"message": __("Oops! Something went wrong while fetching Statement of Accounts"),
					"indicator": "red"
				})

				// if any error ocurrs, make sure to clear the table
				frm.set_value("statement_of_accounts", new Array())
			}
		).always(_ => {
			frappe.dom.unfreeze()
			frm._fetching_statement_of_accounts = false
			frm.dirty()
		})
	}

	
	frappe.ui.form.on("Statement of Accounts", {
		refresh, customer, as_of_date,
	})
}