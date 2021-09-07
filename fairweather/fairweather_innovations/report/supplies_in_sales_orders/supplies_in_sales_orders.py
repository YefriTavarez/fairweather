# -*- coding: utf-8 -*-
# Copyright (c) 2021, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import fairweather

from frappe import db as database
from frappe import _ as translate

from frappe.utils import flt, today


class SuppliesInSalesOrders:
    @classmethod
    def run(cls, filters):
        cls.freight_item = None
        # cls.dynamic_cols = cls.get_dynamic_cols(filters)

        return cls.get_columns(filters), \
            cls.get_data(filters)

    @classmethod
    def get_columns(cls, filters):
        columns = list()

        # sales_order
        # customer
        # item_group
        # item_code
        # description
        # qty
        # amount
        # bom

        columns += [cls.get_docfield("Sales Order", "Link", "Sales Order")]
        columns += [cls.get_docfield("Transaction Date", "Date")]
        columns += [cls.get_docfield("Status")]
        columns += [cls.get_docfield("Customer", "Link", "Customer", length=260)]

        columns += [cls.get_docfield("BOM", "Link", "BOM", length=180)]
        columns += [cls.get_docfield("Item", "Link", "Item")]
        columns += [cls.get_docfield("Description", length=300)]
        columns += [cls.get_docfield("Qty", "Int")]
        columns += [cls.get_docfield("Rate", "Currency")]
        columns += [cls.get_docfield("Amount", "Currency")]
        columns += [cls.get_docfield("Item Group", "Link", "Item Group", length=150)]

        # columns += cls.dynamic_cols

        # columns += [cls.get_docfield("Total Taxes and Charges", "Currency")]
        # columns += [cls.get_docfield("Grand Total", "Currency")]
        # columns += [cls.get_docfield("Outstanding Amount", "Currency")]

        return columns

    @classmethod
    def get_data(cls, filters, as_list=True):
        conditions = cls.get_conditions(filters)

        result = cls.get_result_set(filters, conditions)

        # doctype = "Sales Taxes and Charges"
        # fieldname = "tax_amount"
        # filters = {
        #     "parenttype": "Sales Order",
        #     "parentfield": "taxes",
        # }

        # for d in result:
        #     d["freight_amount"] = cls.get_freight_amount(d)

        #     for account in cls.dynamic_cols:
        #         filters.update({
        #             "parent": d.sales_invoice,
        #             "description": account,
        #             })

        #         value = frappe.get_value(doctype, filters, fieldname)

        #         d[frappe.scrub(account)] = value or 0.000

        if as_list:
            return cls.as_list(result)

        return result

    @classmethod
    def get_result_set(cls, filters, conditions):
        query = cls.get_query(conditions)
        # cls.include_item_group_in_filters(filters)

        return database.sql(query, filters, as_dict=True)

    @classmethod
    def get_dynamic_cols(cls, filters):
        conditions = cls.get_conditions(filters, ignore_item_groups=True)

        query = """
            Select
                distinct(
                    `tabSales Taxes and Charges`.`description`
                ) As account
            From
                `tabSales Taxes and Charges`,
                `tabSales Order`,
                `tabSales Order Item`,
                `tabAddress`
            Where
                `tabSales Taxes and Charges`.`parenttype` = "Sales Order"
                And `tabSales Taxes and Charges`.`parentfield` = "taxes"
                And `tabSales Taxes and Charges`.`parent` = `tabSales Order`.`name`
                And {conditions}
        """.format(conditions=conditions)

        # frappe.errprint(query)

        return database.sql_list(query, filters)

    @classmethod
    def include_item_group_in_filters(cls, filters):
        filters.update({
            "item_groups": fairweather.get_sales_by_state_items_groups(),
        })
        

    @classmethod
    def get_query(cls, conditions):
        return """
            Select
                `tabSales Order`.`name` As sales_order,
                `tabSales Order`.`transaction_date`,
                `tabSales Order`.`status`,
                `tabSales Order`.`customer`,
                `tabBOM`.`name` As bom,
                `tabSales Order Item`.`item_code`,
                `tabSales Order Item`.`description`,
                `tabSales Order Item`.`qty`,
                `tabSales Order Item`.`rate`,
                `tabSales Order Item`.`amount`,
                `tabSales Order Item`.`item_group`
            From 
                `tabSales Order`
            Inner Join
                `tabSales Order Item`
                On
                    `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                    And `tabSales Order Item`.`parentfield` = "items"
                    And `tabSales Order Item`.`parenttype` = "Sales Order"
            Inner Join
                `tabBOM`
            Inner Join
                `tabBOM Item`
                On
                    `tabBOM Item`.`parent` = `tabBOM`.`name`
                    And `tabBOM Item`.`parentfield` = "items"
                    And `tabBOM Item`.`parenttype` = "BOM"
            Where
                {conditions}
            Order By
                sales_order Asc
        """.format(conditions=conditions)

        # `tabSales Order Item`.`item_code` = `tabBOM`.`item`
        #     And `tabSales Order`.`docstatus` = 1
        #     And `tabBOM Item`.`item_code` = %(supply_item)s

    @classmethod
    def get_conditions(cls, filters, ignore_item_groups=False):
        conditions = list()

        if True:
            conditions += ["`tabBOM`.`item` = `tabSales Order Item`.`item_code`"]

        # if not ignore_item_groups:
        #     conditions += ["`tabSales Order Item`.`item_group` in %(item_groups)s"]

        if filters.get("company"):
            conditions += ["`tabSales Order`.`company` = %(company)s"]

        if filters.get("from_date"):
            conditions += ["`tabSales Order`.`transaction_date` >= %(from_date)s"]

        if filters.get("to_date"):
            conditions += ["`tabSales Order`.`transaction_date` <= %(to_date)s"]

        if filters.get("supply_item"):
            conditions += ["`tabBOM Item`.`item_code` = %(supply_item)s"]

        if filters.get("bom"):
            conditions += ["`tabBOM`.`name` = %(bom)s"]

        if filters.get("customer"):
            conditions += ["`tabSales Order`.`customer` = %(customer)s"]

        if filters.get("include_draft_orders"):
            conditions += ["`tabSales Order`.`docstatus` in (0, 1)"]
        else:
            conditions += ["`tabSales Order`.`docstatus` = 1"]

        return " And ".join(conditions)

    @classmethod
    def get_docfield(cls, label, fieldtype="Data", options="", length=100):
        kwargs = {
            "label": translate(label),
            "fieldtype": fieldtype,
            "options": options,
            "length": length,
        }

        return "{label}:{fieldtype}/{options}:{length}" \
            .format(**kwargs)

    @classmethod
    def get_field_list(cls):
        fieldlist = [
            "sales_order",
            "transaction_date",
            "status",
            "customer",
            "bom",
            "item_code",
            "description",
            "qty",
            "rate",
            "amount",
            "item_group",
        ]

        # fieldlist += [frappe.scrub(col) for col in cls.dynamic_cols]

        # fieldlist += [
        #     "total_taxes_and_charges",
        #     "grand_total",
        #     "outstanding_amount",
        # ]
        
        return fieldlist

    @classmethod
    def as_list(cls, data):
        array = list()

        for d in data:
            array += [cls.to_list(d)]

        return array

    @classmethod
    def to_list(cls, data):
        array = list()

        for d in cls.get_field_list():
            array += [data[d]]

        return array

    @classmethod
    def get_freight_item(cls):
        doctype = "Stock Settings"
        fieldname = "freight_item"

        if not cls.freight_item:
            cls.freight_item = database \
                .get_single_value(doctype, 
                    fieldname, cache=True)

        return cls.freight_item

    @classmethod
    def get_freight_amount(cls, row):
        freight_item = cls.get_freight_item()

        doctype = "Sales Order Item"
 
        filters = {
            "parentfield": "items",
            "parenttype": "Sales Order",
            "parent": row.sales_invoice,
            "item_code": freight_item,
        }

        fieldname = "net_amount"


        value = frappe.get_value(doctype, filters, fieldname)

        return value or 0.000



def execute(filters=None):
    return SuppliesInSalesOrders \
        .run(filters)


# -- Filter orders by date range
# -- Filter Order by Customer
# -- Filter by Supply Item Code
# -- Filter by BOM
# -- Include Draft Orders
# -- `tabBOM Item`.`item_code` = `tabBOM`.`item`
# Select
# 	`tabSales Order`.`name` As sales_order,
# 	`tabSales Order`.`transaction_date`,
# 	`tabSales Order`.`customer`,
# 	`tabSales Order Item`.`item_group`,
# 	`tabSales Order Item`.`item_code`,
# 	`tabSales Order Item`.`description`,
# 	`tabSales Order Item`.`qty`,
# 	`tabSales Order Item`.`amount`,
# 	`tabBOM`.`name` As bom
# From 
# 	`tabSales Order`
# Inner Join
# 	`tabSales Order Item`
# 	On
# 		`tabSales Order Item`.`parent` = `tabSales Order`.`name`
# 		And `tabSales Order Item`.`parentfield` = "items"
# 		And `tabSales Order Item`.`parenttype` = "Sales Order"
# Inner Join
# 	`tabBOM`
# Inner Join
# 	`tabBOM Item`
# 	On
# 		`tabBOM Item`.`parent` = `tabBOM`.`name`
# 		And `tabBOM Item`.`parentfield` = "items"
# 		And `tabBOM Item`.`parenttype` = "BOM"

# Where
# 	`tabSales Order Item`.`item_code` = `tabBOM`.`item`
# 	And `tabSales Order`.`docstatus` = 1
# 	And `tabBOM Item`.`item_code` = %(supply_item)s
# ;

# filters = {
# 	"from_date": "2021-01-01",
# 	"to_date": "2021-04-31",
# 	"supply_item": "CG1R02"
# 	"customer": None,
# 	"bom": None,
# 	"include_draft": False,
# }