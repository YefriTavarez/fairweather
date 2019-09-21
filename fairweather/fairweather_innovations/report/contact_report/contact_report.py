# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database

def execute(filters=None):
    return get_column(filters), \
        get_data(filters)

def get_column(filters=None):
    return (
        "Customer:Link/Customer:120",
        "Customer Name:Data:120",
        "Customer Group:Link/Customer Group:100",
        "Salutation:Data:50",
        "First Name:Data:120",
        "Last Name:Data:120",
        "Email:Data:180",
        "Contact Role:Link/Contact Role:140",
        "Phone:Data:120",
    )

def get_data(filters=None):
    conditions = get_conditions(filters)
    optional_join = get_optional_join(filters)

    return database.sql("""
        Select
            `tabCustomer`.`name`,
            `tabCustomer`.`customer_name`,
            `tabCustomer`.`customer_group`,
            `tabContact`.`salutation`,
            `tabContact`.`first_name`,
            `tabContact`.`last_name`,
            `tabContact`.`email_id`,
            `tabContact`.`contact_role`,
            `tabContact`.`phone`
        From
            `tabContact`
        Inner Join
            `tabDynamic Link`
            On
                `tabDynamic Link`.`parent` = `tabContact`.`name`
                And `tabDynamic Link`.`parenttype` = "Contact"
                And `tabDynamic Link`.`parentfield` = "links"
        Inner Join
            `tabCustomer`
            On
                `tabDynamic Link`.`link_doctype` = "Customer"
                And `tabDynamic Link`.`link_name` = `tabCustomer`.`name`
        Where
            {conditions}
    """.format(optional_join=optional_join, 
        conditions=conditions), filters, as_list=True)

def get_optional_join(filters=None):
    if "customer_group" in filters:
        return """
            
        """

    return ""

def get_conditions(filters=None):
    conditions = list()

    conditions += ["1 = 1"]

    if "customer_group" in filters:
        conditions += ["`tabCustomer`.`customer_group` = %(customer_group)s"]

    if "contact_role" in filters:
        conditions += ["`tabContact`.`contact_role` = %(contact_role)s"]

    return " And ".join(conditions)
