# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database

class SalesDetailByCustomer:
    @classmethod
    def run(cls, filters):
        return cls.getcolumns(filters), cls.getdata(filters)

    @classmethod
    def getcolumns(cls, filters):
        columns = list()

        customer_df = cls.getdocfield("Customer", "Link", "Customer")
        if not filters.get("customer"):
            columns.append(customer_df)

        fixed_cols = [
            cls.getdocfield("Item", "Link", "Item"),
            cls.getdocfield("Item Description", "Data"),	
            cls.getdocfield("Qty", "Int"),
            cls.getdocfield("UOM", "Link", "UOM"),
            cls.getdocfield("Rate (Avg)", "Currency"),
            cls.getdocfield("Rate (STD Deviation)", "Float"),
            cls.getdocfield("Rate (Variance)", "Float"),
            cls.getdocfield("Amount", "Currency"),
        ]

        columns.extend(fixed_cols)

        return columns

    @classmethod
    def getdata(cls, filters):
        conditions = cls.getconditions(filters)

        data = database.sql(
            """
                Select
                    `tabSales Invoice`.`customer` As customer,
                    `tabSales Invoice Item`.`item_code` As item_code,
                    `tabSales Invoice Item`.`description` As item_description,
                    Sum(`tabSales Invoice Item`.`stock_qty`) As stock_qty,
                    `tabSales Invoice Item`.`stock_uom` As stock_uom,
                    Avg(`tabSales Invoice Item`.`rate`) As avgrate,
                    StdDev(`tabSales Invoice Item`.`rate`) As stddevrate,
                    Variance(`tabSales Invoice Item`.`rate`) As varrate,
                    Sum(`tabSales Invoice Item`.`amount`) As amount
                From
                    `tabItem`
                Inner Join
                    `tabSales Invoice Item`
                    On
                        `tabItem`.`name` = `tabSales Invoice Item`.`item_code`
                Inner Join
                    `tabSales Invoice`
                    On
                        `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
                        And `tabSales Invoice Item`.`parenttype` = "Sales Invoice"
                        And `tabSales Invoice Item`.`parentfield` = "items"
                Where
                    {conditions}
                Group By
                    `tabSales Invoice Item`.`item_code`
            """.format(conditions=conditions), 
        filters, as_dict=True)

        return cls.preprocess(data, filters)
        

    @classmethod
    def preprocess(cls, data, filters):

        return cls.as_list(data, filters)

    @classmethod
    def as_list(cls, data, filters):
        newlist = list()

        sortedfields = cls.sortedfields(filters)

        def sortrow(datarow):
            sortedrow = list()

            for fieldname in sortedfields:
                value = datarow \
                    .get(fieldname)

                sortedrow.append(value)

            return sortedrow

        for datarow in data:
            sortedrow = sortrow(datarow)
            newlist.append(sortedrow)

        return newlist

    @classmethod
    def sortedfields(cls, filters):
        fieldlist = list()

        if not filters.get("customer"):
            fieldlist.append("customer")

        fixed_cols = [
            "item_code",
            "item_description",
            "stock_qty",
            "stock_uom",
            "avgrate",
            "stddevrate",
            "varrate",
            "amount",
        ]

        fieldlist.extend(fixed_cols)

        return fieldlist
    
    @classmethod
    def getconditions(cls, filters):
        conditions = list()

        conditions.append("`tabSales Invoice`.`docstatus` = 1")

        if filters.get("customer"):
            conditions.append("`tabSales Invoice`.`customer` = %(customer)s")

        if filters.get("from_date"):
            conditions.append("`tabSales Invoice`.`posting_date` >= %(from_date)s")

        if filters.get("to_date"):
            conditions.append("`tabSales Invoice`.`posting_date` <= %(to_date)s")

        return " And ".join(conditions)
        

    @classmethod
    def getdocfield(cls, label, fieldtype="Data", options=None, width=120):
        return "{label}:{fieldtype}/{options}:{width}" \
            .format(label=label, fieldtype=fieldtype, options=options, width=width)

def execute(filters=None):
    return SalesDetailByCustomer \
        .run(filters)
