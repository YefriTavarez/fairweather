# -*- coding: utf-8 -*-
# Copyright (c) 2020, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import fairweather

from frappe import db as database
from frappe import _ as translate

from frappe.utils import flt, today


class SalesByState:
    @classmethod
    def run(cls, filters):
        cls.freight_item = None
        cls.dynamic_cols = cls.get_dynamic_cols(filters)

        return cls.get_columns(filters), \
            cls.get_data(filters)

    @classmethod
    def get_columns(cls, filters):
        columns = list()

        columns += [cls.get_docfield("Sales Invoice", "Link", "Sales Invoice")]
        columns += [cls.get_docfield("Posting Date", "Date")]
        columns += [cls.get_docfield("Customer", "Link", "Customer", length=200)]
        columns += [cls.get_docfield("Account", "Link", "Account", length=150)]

        columns += [cls.get_docfield("State", "Link", "State")]
        columns += [cls.get_docfield("Address Line", length=240)]
        columns += [cls.get_docfield("Postal Code")]
        columns += [cls.get_docfield("City")]
        columns += [cls.get_docfield("Address Type")]
        columns += [cls.get_docfield("Freight Amount", "Currency")]
        columns += [cls.get_docfield("Net Total", "Currency")]

        columns += cls.dynamic_cols

        columns += [cls.get_docfield("Total Taxes and Charges", "Currency")]
        columns += [cls.get_docfield("Grand Total", "Currency")]
        columns += [cls.get_docfield("Outstanding Amount", "Currency")]

        # columns += [cls.get_docfield("Paid_amount", "Currency")]
        # columns += [cls.get_docfield("Write_off_amount", "Currency")]

        return columns

    @classmethod
    def get_data(cls, filters, as_list=True):
        conditions = cls.get_conditions(filters)

        result = cls.get_result_set(filters, conditions)

        doctype = "Sales Taxes and Charges"
        fieldname = "tax_amount"
        filters = {
            "parenttype": "Sales Invoice",
            "parentfield": "taxes",
        }

        for d in result:
            d["freight_amount"] = cls.get_freight_amount(d)

            for account in cls.dynamic_cols:
                filters.update({
                    "parent": d.sales_invoice,
                    "description": account,
                    })

                value = frappe.get_value(doctype, filters, fieldname)

                d[frappe.scrub(account)] = value or 0.000

        if as_list:
            return cls.as_list(result)

        return result

    @classmethod
    def get_result_set(cls, filters, conditions):
        query = cls.get_query(conditions)
        cls.include_item_group_in_filters(filters)

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
                `tabSales Invoice`,
                `tabSales Invoice Item`,
                `tabAddress`
            Where
                `tabSales Taxes and Charges`.`parenttype` = "Sales Invoice"
                And `tabSales Taxes and Charges`.`parentfield` = "taxes"
                And `tabSales Taxes and Charges`.`parent` = `tabSales Invoice`.`name`
                And {conditions}
        """.format(conditions=conditions)

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
                `tabSales Invoice`.`name` As sales_invoice,
                `tabSales Invoice`.`posting_date`,
                `tabSales Invoice`.`customer`,
                `tabSales Invoice`.`debit_to`,
                `tabAddress`.`state`,
                `tabAddress`.`address_line1`,
                `tabAddress`.`pincode`,
                `tabAddress`.`city`,
                `tabAddress`.`address_type`,
                `tabSales Invoice`.`net_total` As freight_amount,
                `tabSales Invoice`.`net_total`,
                `tabSales Invoice`.`total_taxes_and_charges`,
                `tabSales Invoice`.`grand_total`,
                `tabSales Invoice`.`outstanding_amount`
            From
                `tabSales Invoice`,
                `tabSales Invoice Item`,
                `tabAddress`                   
            Where
                {conditions}
                And `tabSales Invoice Item`.`parenttype` = "Sales Invoice"
                And `tabSales Invoice Item`.`parentfield` = "items"
                And `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
            Group By
                `tabSales Invoice`.`name`
            Order By
                `tabSales Invoice`.`name` Asc
        """.format(conditions=conditions)

    @classmethod
    def get_conditions(cls, filters, ignore_item_groups=False):
        conditions = list()

        conditions += ["`tabSales Invoice`.`docstatus` = 1"]

        if not ignore_item_groups:
            conditions += ["`tabSales Invoice Item`.`item_group` in %(item_groups)s"]

        if "from_date" in filters:
            conditions += ["`tabSales Invoice`.`posting_date` >= %(from_date)s"]

        if "to_date" in filters:
            conditions += ["`tabSales Invoice`.`posting_date` <= %(to_date)s"]

        if "customer" in filters:
            conditions += ["`tabSales Invoice`.`customer` = %(customer)s"]

        if "state" in filters:
            conditions += ["`tabAddress`.`state` = %(state)s"]

        address_type = filters.get("address_type")

        if address_type == "Billing":
            conditions += ["`tabSales Invoice`.`customer_address` = `tabAddress`.`name`"]
        elif address_type == "Shipping":
            conditions += ["`tabSales Invoice`.`shipping_address_name` = `tabAddress`.`name`"]
        else:
            conditions += ["`tabAddress`.`name` in (`tabSales Invoice`.`customer_address`, `tabSales Invoice`.`shipping_address_name`)"]


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
            "sales_invoice",
            "posting_date",
            "customer",
            "debit_to",
            "state",
            "address_line1",
            "pincode",
            "city",
            "address_type",
            "freight_amount",
            "net_total",
        ]

        fieldlist += [frappe.scrub(col) for col in cls.dynamic_cols]

        fieldlist += [
            "total_taxes_and_charges",
            "grand_total",
            "outstanding_amount",
        ]
        
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

        doctype = "Sales Invoice Item"
 
        filters = {
            "parentfield": "items",
            "parenttype": "Sales Invoice",
            "parent": row.sales_invoice,
            "item_code": freight_item,
        }

        fieldname = "net_amount"


        value = frappe.get_value(doctype, filters, fieldname)

        return value or 0.000



def execute(filters=None):
    return SalesByState \
        .run(filters)
