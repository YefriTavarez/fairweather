# -*- coding: utf-8 -*-
# Copyright (c) 2020, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
import fairweather

from frappe import db
from frappe import _ as translate

from frappe import utils
from functools import lru_cache


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
        columns += [cls.get_docfield("Customer",
                                     "Link", "Customer", length=200)]
        columns += [cls.get_docfield("Account", "Link", "Account", length=150)]

        columns += [cls.get_docfield("State", "Link", "State")]
        columns += [cls.get_docfield("Address Line", length=240)]
        columns += [cls.get_docfield("Postal Code")]
        columns += [cls.get_docfield("City")]
        columns += [cls.get_docfield("Address Type")]
        columns += [cls.get_docfield("Freight Amount", "Currency")]
        columns += [cls.get_docfield("Net Total", "Currency")]

        columns += [d[0] for d in cls.dynamic_cols]

        columns += [cls.get_docfield("Total Taxes and Charges", "Currency")]
        columns += [cls.get_docfield("Grand Total", "Currency")]
        columns += [cls.get_docfield("Outstanding Amount", "Currency")]

        # columns += [cls.get_docfield("Paid_amount", "Currency")]
        # columns += [cls.get_docfield("Write_off_amount", "Currency")]

        return columns

    @classmethod
    def get_tax_amount(cls, charge, row, real):
        return row.sales_invoice == charge.parent \
            and charge.description == real

    @classmethod
    def get_data(cls, filters, as_list=True):
        conditions = cls.get_conditions(filters)

        results = cls.get_result_set(filters, conditions)
        all_charges = cls.get_taxes(filters)

        for row in results:
            row.freight_amount = cls.get_freight_amount(row)
            for fancy, real in cls.dynamic_cols:
                iterator = filter(
                    lambda charge: cls.get_tax_amount(charge, row, real),
                    all_charges
                )

                tax_amount = sum(
                    [utils.flt(charge.tax_amount) for charge in iterator]
                )

                row[frappe.scrub(fancy)] = tax_amount

        if as_list:
            return cls.as_list(results)

        return results

    @classmethod
    def get_taxes(cls, filters):
        def _get_conditions():
            conditions = list()

            conditions += ["invoice.docstatus = 1"]

            if filters.from_date:
                conditions += ["invoice.posting_date >= %(from_date)s"]

            if filters.to_date:
                conditions += ["invoice.posting_date <= %(to_date)s"]

            if filters.customer:
                conditions += ["invoice.customer = %(customer)s"]

            return " And ".join(conditions)

        return db.sql(f"""
            Select
                charges.parent,
                Replace(charges.description, "\n", "") As description,
                charges.tax_amount
            From
                `tabSales Taxes and Charges` As charges,
                `tabSales Invoice` As invoice
            Where
                charges.parenttype = "Sales Invoice"
                And charges.parentfield = "taxes"
                And charges.parent = invoice.name
                And {_get_conditions()}
        """, filters, as_dict=True)

    @classmethod
    def get_result_set(cls, filters, conditions):
        query = cls.get_query(conditions)
        cls.include_item_group_in_filters(filters)

        return db.sql(query, filters, as_dict=True)

    @classmethod
    def get_dynamic_cols(cls, filters):
        conditions = cls.get_conditions(filters, ignore_item_groups=True)

        query = """
            Select
                Distinct(
                    Replace(charges.description, "\n", "")
                )
            From
                `tabSales Taxes and Charges` As charges,
                `tabSales Invoice` As invoice,
                `tabAddress` As address
            Where
                charges.parenttype = "Sales Invoice"
                And charges.parentfield = "taxes"
                And charges.parent = invoice.name
                And charges.tax_amount != 0
                And IfNull(charges.description, "") != ""
                And {conditions}
        """.format(conditions=conditions)

        def make_it_fancy(value):
            return utils.cstr(value) \
                .replace("State:", "") \
                .replace("County:", "") \
                .replace("\t", "") \
                .strip()

        return [(make_it_fancy(d), d) for d in db.sql_list(query, filters)]

    @classmethod
    def include_item_group_in_filters(cls, filters):
        filters.update({
            "item_groups": fairweather.get_sales_by_state_items_groups(),
        })

    @classmethod
    def get_query(cls, conditions):
        return """
            Select
                invoice.name As sales_invoice,
                invoice.posting_date,
                invoice.customer,
                invoice.debit_to,
                address.state,
                address.address_line1,
                address.pincode,
                address.city,
                address.address_type,
                invoice.net_total As freight_amount,
                invoice.net_total,
                invoice.total_taxes_and_charges,
                invoice.grand_total,
                invoice.outstanding_amount
            From
                `tabSales Invoice` As invoice,
                `tabSales Invoice Item` As item,
                `tabAddress` As address
            Where
                {conditions}
                And item.parenttype = "Sales Invoice"
                And item.parentfield = "items"
                And item.parent = invoice.name
            Group By
                invoice.name
            Order By
                invoice.name Asc
        """.format(conditions=conditions)

    @classmethod
    def get_conditions(cls, filters, ignore_item_groups=False):
        conditions = list()

        conditions += ["invoice.docstatus = 1"]

        if not ignore_item_groups:
            conditions += ["item.item_group in %(item_groups)s"]

        if "from_date" in filters:
            conditions += ["invoice.posting_date >= %(from_date)s"]

        if "to_date" in filters:
            conditions += ["invoice.posting_date <= %(to_date)s"]

        if "customer" in filters:
            conditions += ["invoice.customer = %(customer)s"]

        if "state" in filters:
            conditions += ["address.state = %(state)s"]

        address_type = filters.get("address_type")

        if address_type == "Billing":
            conditions += ["invoice.customer_address = address.name"]
        elif address_type == "Shipping":
            conditions += ["invoice.shipping_address_name = address.name"]
        else:
            conditions += [
                "address.name in (invoice.customer_address, invoice.shipping_address_name)"]

        return " And ".join(conditions)

    @classmethod
    def get_docfield(cls, label, fieldtype="Data", options="", length=100):
        return f"{label}:{fieldtype}/{options}:{length}"

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

        fieldlist += [frappe.scrub(col[0]) for col in cls.dynamic_cols]

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
            cls.freight_item = db \
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
