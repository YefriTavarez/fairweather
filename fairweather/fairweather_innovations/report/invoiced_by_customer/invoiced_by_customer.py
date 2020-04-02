# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database
from frappe import _ as translate

from frappe.utils import flt, today

class InvoicedByCustomer:
    @classmethod
    def run(cls, filters):
        return cls.get_columns(filters), \
            cls.get_data(filters)

    @classmethod
    def get_columns(cls, filters):
        columns = list()

        columns += [cls.get_docfield("Customer", "Link", "Customer", 200)]

        columns += [cls.get_docfield("Net Total", "Currency")]
        columns += [cls.get_docfield("Total Taxes and Charges", "Currency")]
        columns += [cls.get_docfield("Grand Total", "Currency")]
        columns += [cls.get_docfield("Outstanding Amount", "Currency")]
        columns += [cls.get_docfield("Paid Amount", "Currency")]
        columns += [cls.get_docfield("Write Off Amount", "Currency")]

        return columns

    @classmethod
    def get_data(cls, filters, as_list=True):
        conditions = cls.get_conditions(filters)

        result = cls.get_result_set(filters, conditions)

        for d in result:
            cls.set_missing_values(filters, d)

        if as_list:
            return cls.as_list(result)

        return result

    @classmethod
    def get_result_set(cls, filters, conditions):
        query = cls.get_query(conditions)

        return database.sql(query, filters, as_dict=True)

    @classmethod
    def get_conditions(cls, filters, ignore_filters=list()):
        conditions = list()

        conditions += ["docstatus = 1"]

        if "from_date" in filters \
            and "from_date" not in ignore_filters:
            conditions += ["posting_date >= %(from_date)s"]

        if "to_date" in filters \
            and "to_date" not in ignore_filters:
            conditions += ["posting_date <= %(to_date)s"]

        if "customer" in filters \
            and "customer" not in ignore_filters:
            conditions += ["customer = %(customer)s"]

        return " And ".join(conditions)

    @classmethod
    def get_query(cls, conditions):
        return """
            Select
                customer,
                Sum(net_total) As net_total,
                Sum(total_taxes_and_charges) As total_taxes_and_charges,
                Sum(grand_total) As grand_total,
                Sum(outstanding_amount) As outstanding_amount,
                0.000 As paid_amount,
                0.000 As write_off_amount
            From
                `tabSales Invoice`
            Where
                {conditions}
            Group By
                customer
        """.format(conditions=conditions)

    @classmethod
    def set_missing_values(cls, filters, data):
        data.paid_amount = cls.get_paid_amount(filters, data)
        data.write_off_amount = cls.get_discount_amount(data.customer, 
            filters.get("to_date"))

    @classmethod
    def get_paid_amount(cls, filters, data):
        conditions = cls.get_conditions(filters, ignore_filters=["customer"])

        if not conditions:
            conditions += "1 = 1"

        customer = database.escape(data.customer)

        conditions += " And party_type = 'Customer'"
        conditions += " And party = '{0}'".format(customer)

        result = database.sql("""
            Select
                Sum(If(payment_type="Receive", paid_amount, 0.000))
                    - Sum(If(payment_type="Pay", paid_amount, 0.000)) balance
            From
                `tabPayment Entry`
            Where
                {conditions}
        """.format(conditions=conditions), filters)

        return result[0][0] if result else 0.000

    @classmethod
    def get_discount_amount(cls, customer, as_of_date=today()):
        values = {
            "posting_date": as_of_date,
            "customer": customer,
        }

        result = database.sql("""
            Select
                Sum(child.credit_in_account_currency)
            From
                `tabJournal Entry` parent
            Inner Join
                `tabJournal Entry Account` child
                On
                    child.parent = parent.name
                    And child.parenttype = "Journal Entry"
                    And child.parentfield = "accounts"
            Where
                parent.docstatus = 1
                And parent.voucher_type = "Write Off Entry"
                And parent.posting_date <= %(posting_date)s
                And child.party_type = "Customer"
                And child.party = %(customer)s
        """, values)

        return result[0][0] if result else 0.000

    @classmethod
    def get_docfield(cls, label, fieldtype="Data", options="", length=120):
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
        return (
            "customer",
            "net_total",
            "total_taxes_and_charges",
            "grand_total",
            "outstanding_amount",
            "paid_amount",
            "write_off_amount",
        )

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


def execute(filters=None):
    return InvoicedByCustomer \
        .run(filters)
