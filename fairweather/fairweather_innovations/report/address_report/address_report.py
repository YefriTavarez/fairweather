# Copyright (c) 2021, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database

def execute(filters=None):
    return get_column(filters), \
        get_data(filters)

def get_column(filters=None):
    from . import columns

    return ["{label}:{fieldtype}/{options}:100".format(**column) for column in columns]

def get_data(filters=None):
    conditions = get_conditions(filters)
    optional_join = get_optional_join(filters)

    return database.sql("""
        Select
            `tabCustomer`.`name`,
            `tabCustomer`.`customer_name`,
            `tabCustomer`.`customer_group`,
            `tabParty Account`.`account`,
            `tabAddress`.`address_title`,
            `tabAddress`.`address_type`,
            `tabAddress`.`address_line1`,
            `tabAddress`.`address_line2`,
            `tabAddress`.`city`,
            `tabAddress`.`county`,
            `tabAddress`.`state`,
            `tabAddress`.`country`,
            `tabAddress`.`pincode`,
            `tabAddress`.`email_id`,
            `tabAddress`.`phone`,
            `tabAddress`.`fax`,
            `tabAddress`.`is_primary_address`,
            `tabAddress`.`is_shipping_address`
        From
            `tabAddress`
        Inner Join
            `tabDynamic Link`
            On
                `tabDynamic Link`.`parent` = `tabAddress`.`name`
                And `tabDynamic Link`.`parenttype` = "Address"
                And `tabDynamic Link`.`parentfield` = "links"
        Inner Join
            `tabCustomer`
            On
                `tabDynamic Link`.`link_doctype` = "Customer"
                And `tabDynamic Link`.`link_name` = `tabCustomer`.`name`

        Inner Join
            `tabParty Account`
            On
                `tabParty Account`.parenttype = "Customer"
                And `tabParty Account`.parentfield = "accounts"
                And `tabParty Account`.parent = `tabCustomer`.`name`
        Where
            {conditions}
    """.format(optional_join=optional_join, 
        conditions=conditions), filters, as_list=True)

def get_optional_join(filters=None):
    if "account" in filters:
        return """
        """

    return ""

def get_conditions(filters=None):
    conditions = list()

    conditions += ["1 = 1"]

    if "customer_group" in filters:
        conditions += ["`tabCustomer`.`customer_group` = %(customer_group)s"]

    if "customer_type" in filters:
        conditions += ["`tabCustomer`.`customer_type` = %(customer_type)s"]

    if "account" in filters:
        conditions += ["`tabParty Account`.`account` = %(account)s"]

    return " And ".join(conditions)
