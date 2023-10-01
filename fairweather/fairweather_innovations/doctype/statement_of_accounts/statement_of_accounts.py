# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from fairweather.fairweather_innovations.report.statement_of_accounts import (
    StatementOfAccounts,
)
from frappe.model.document import Document


class StatementofAccounts(Document):
	@frappe.whitelist()
	def fetch_statement_of_accounts(self, throw=True):
		filters = self.get_filters()
		statement = StatementOfAccounts(filters)

		self.statement_of_accounts = list()

		if not statement.data and throw:
			frappe.throw("No data found for the given criteria")

		self.append_statement_of_accounts(statement.data)

	def append_statement_of_accounts(self, data):
		for row in data:
			self.append("statement_of_accounts", {
				"posting_date": row.posting_date,
				"sales_invoice": row.name,
				"grand_total": row.grand_total,
				"due_date": row.due_date,
				"outstanding_amount": row.outstanding_amount,
			})

	def get_filters(self):
		filters = dict(
			company=frappe.defaults.get_user_default("Company"),
			customer=self.customer,
			to_date=self.as_of_date,
		)

		return filters
