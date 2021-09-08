# Copyright (c) 2021, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database

# from frappe.utils import flt, cint, cstr


class SalesByItem:
    @classmethod
    def run(cls, filters):
        cls.filters = filters

        cls.setup_conditions()

        cls.setup_columns()
        cls.setup_data()

        return cls.columns, cls.data

    @classmethod
    def setup_columns(cls):
        cls.columns = [
            "Item:Link/Item:200",
            "Item Group:Link/Item Group:200",
            "Qty:Float:100",
            "Avg Rate:Currency:100",
            "Min Rate:Currency:100",
            "Max Rate:Currency:100",
            "Total Sales:Currency:100",
        ]

    @classmethod
    def setup_data(cls):
        data = cls.get_main_dataset()

        cls.data = cls.as_list(data)

    @classmethod
    def setup_conditions(cls):
        cls.conditions = cls.get_conditions()

    @classmethod
    def get_main_dataset(cls):
        cls.setup_query()
        resultset = database \
            .sql(cls.query, cls.filters, as_dict=True)

        return cls.postprocess(resultset)

    @classmethod
    def postprocess(cls, resultset):
        # addional processing of results
        # goes here.
        return resultset

    @classmethod
    def setup_query(cls):
        cls.query = """
            Select
                sales_invoice_item.item_code,
                sales_invoice_item.item_group,
                Sum(sales_invoice_item.qty) As qty,
                Avg(sales_invoice_item.rate) As avg_rate,
                Min(sales_invoice_item.rate) As min_rate,
                Max(sales_invoice_item.rate) As max_rate,
                Sum(sales_invoice_item.amount) As total_sales
            From
                `tabSales Invoice` sales_invoice
            Inner Join
                `tabSales Invoice Item` sales_invoice_item
                On
                    sales_invoice_item.parent = sales_invoice.name
                    And sales_invoice_item.parenttype = 'Sales Invoice'
                    And sales_invoice_item.parentfield = 'items'
            Where
                {conditions}
            Group By
                sales_invoice_item.item_code
            Order By
                qty Desc
        """.format(conditions=cls.conditions)

    @classmethod
    def get_conditions(cls):
        conditions = list()

        # always conditions
        conditions.append("sales_invoice.docstatus = 1")
        conditions.append("sales_invoice_item.rate > 0")
        conditions.append("sales_invoice_item.qty > 0")

        if cls.filters.get("company"):
            conditions.append(
                "sales_invoice.company >= %(company)s"
            )

        if cls.filters.get("from_date"):
            conditions.append(
                "sales_invoice.posting_date >= %(from_date)s"
            )

        if cls.filters.get("to_date"):
            conditions.append(
                "sales_invoice.posting_date <= %(to_date)s"
            )

        if cls.filters.get("item"):
            conditions.append(
                "sales_invoice_item.item_code = %(item)s"
            )

        if cls.filters.get("item_group"):
            conditions.append(
                "sales_invoice_item.item_group = %(item_group)s"
            )

        return " And ".join(conditions)

    @classmethod
    def as_list(cls, data):
        # convert from dict to list
        datalist = list()
        for line in data:
            datalist.append(
                [
                    line.item_code,
                    line.item_group,
                    line.qty,
                    line.avg_rate,
                    line.min_rate,
                    line.max_rate,
                    line.total_sales,
                ]
            )

        return datalist


def execute(filters=None):
    return SalesByItem.run(filters)
