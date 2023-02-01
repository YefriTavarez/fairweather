# -*- coding: utf-8 -*-
# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from frappe import db

from frappe.desk.reportview import get_match_cond, get_filters_cond


@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_len, filters):
    # , "mcond": get_match_cond(doctype)
    values = {
        "txt": "%%%s%%" % txt,
        "_txt": txt.replace("%", ""),
        "start": start,
        "page_len": page_len
    }

    return db.sql(
        f"""
            Select
                Distinct customer.name,
                customer.customer_name,
                customer.customer_group
            From
                `tabCustomer` As customer
            Inner Join
                `tabSales Invoice` As invoice
                On invoice.customer = customer.name
                    And invoice.is_return = 1
                    And invoice.docstatus = 1
                    And invoice.outstanding_amount > 0
            Where
                customer.docstatus < 2
                And customer.disabled = 0
                And (
                    customer.{searchfield} Like %(txt)s
                    Or customer.customer_name Like %(txt)s
                    Or customer.customer_group Like %(txt)s
                )
            Order By
                If(Locate(%(_txt)s, customer.name), Locate(%(_txt)s, customer.name), 99999),
                If(Locate(%(_txt)s, customer.customer_name), Locate(%(_txt)s, customer.customer_name), 99999),
                If(Locate(%(_txt)s, customer.customer_group), Locate(%(_txt)s, customer.customer_group), 99999),
                customer.name, customer.customer_name
            Limit %(start)s, %(page_len)s
        """, values
    )
