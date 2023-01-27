# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from frappe import db, _dict

# hack! to be able to say frappe.as_dict
frappe.as_dict = _dict


def execute(filters=None):
    report = StatementOfAccountsReport(filters)
    return report.run()


class StatementOfAccountsReport(object):
    def __init__(self, filters=None):
        self.filters = filters
        self.columns = self.get_columns()
        self.data = self.get_data()

    def run(self):
        return self.columns, self.data

    def get_columns(self):
        # Cols:
        # Date                  -> Sales Invoice ~ Posting Date
        # Invoice Number        -> Sales Invoice ~ Name
        # Amount                -> Sales Invoice ~ Grand Total
        # Due Date              -> Sales Invoice ~ Due Date
        # Outstanding Balance   -> Sales Invoice ~ Outstanding Amount

        return [
            {
                "label": "Date",
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 100,
            },
            {
                "label": "Invoice Number",
                "fieldname": "name",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "width": 100,
            },
            {
                "label": "Amount",
                "fieldname": "grand_total",
                "fieldtype": "Currency",
                "width": 100,
            },
            {
                "label": "Due Date",
                "fieldname": "due_date",
                "fieldtype": "Date",
                "width": 100,
            },
            {
                "label": "Outstanding Balance",
                "fieldname": "outstanding_amount",
                "fieldtype": "Currency",
                "width": 100,
            },
        ]

    def get_data(self):
        conditions = self.get_conditions()
        data = self.get_sales_invoices(conditions)

        return data

    def get_conditions(self):
        conditions = list()

        # always on conditions
        conditions.append("docstatus = 1")
        conditions.append("outstanding_amount != 0")

        # company
        if self.filters.get("company"):
            conditions.append("company = %(company)s")

        # customer
        if self.filters.get("customer"):
            conditions.append("customer = %(customer)s")

        # from_date
        if self.filters.get("from_date"):
            conditions.append("posting_date >= %(from_date)s")

        # to_date
        if self.filters.get("to_date"):
            conditions.append("posting_date <= %(to_date)s")

        return " And ".join(conditions)

    def get_sales_invoices(self, conditions):
        fields = ", ".join(
            [
                "posting_date",
                "name",
                "grand_total",
                "due_date",
                "outstanding_amount",
            ]
        )

        query = f"""
            Select
                {fields}
            From
                `tabSales Invoice`
            Where
                {conditions}
            Order By
                posting_date
        """

        values = self.filters

        return db.sql(query, values, as_dict=True)
