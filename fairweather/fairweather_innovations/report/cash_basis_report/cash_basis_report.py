# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database
from frappe import _ as translate
from frappe import _dict as pydict

from frappe.utils import flt, cint, cstr

class QueryReport:
    @classmethod
    def run(cls, filters):
        return cls.columns(filters), \
            cls.data(filters)
    
    @classmethod
    def columns(cls, filters):
        columns = list()

        columns += [cls.get_docfield("Invoice Name", "Link", "Sales Invoice")]
        columns += [cls.get_docfield("Invoice Date", "Date")]
        columns += [cls.get_docfield("Due Date", "Date")]
        columns += [cls.get_docfield("Payment Name", "Link", "Payment Entry")]
        columns += [cls.get_docfield("Payment Date", "Date")]
        columns += [cls.get_docfield("Mode of Payment", "Link", "Mode of Payment")]
        columns += [cls.get_docfield("Customer Name", "Link", "Customer", 160)]
        columns += [cls.get_docfield("Customer Group", "Link", "Customer Group", 120)]
        columns += [cls.get_docfield("Currency", "Link", "Currency")]
        columns += [cls.get_docfield("Invoice Total Amount", "Currency")]
        columns += [cls.get_docfield("Invoice Allocated Amount", "Currency")]
        columns += [cls.get_docfield("Invoice Outstanding Amount", "Currency")]

        return columns
    
    @classmethod
    def data(cls, filters):
        conditions = cls.conditions(filters)
        
        data = cls.result(conditions, filters)

        for d in data:
            pass

        return cls.as_list(data)
    

    @classmethod
    def conditions(cls, filters):
        conditions = list()
        
                
        if True: # always conditions
            conditions += ["payment.payment_type = \"Receive\""]

        if True: # always conditions
            conditions += ["payment.party_type = \"Customer\""]

        if "company" in filters:
            conditions += ["payment.company = %(company)s"]
        
        if "from_date" in filters:
            conditions += ["payment.posting_date >= %(from_date)s"]

        if "to_date" in filters:
            conditions += ["payment.posting_date <= %(to_date)s"]
        
        if "customer_group" in filters:
            conditions += ["""payment.party in (
                Select
                    customer.name
                From
                    `tabCustomer` As customer
                Where
                    customer.customer_group = %(customer_group)s)
            """]

        return " And ".join(conditions)
    
    @classmethod
    def result(cls, conditions, values):
        query = """
            Select
                (
                    reference.reference_name
                ) As invoice_name,
                (
                    Select
                        invoice.posting_date
                    From
                        `tabSales Invoice` As invoice
                    Where
                        invoice.name = reference.reference_name
                ) As invoice_date,
                (
                    Select
                        invoice.due_date
                    From
                        `tabSales Invoice` As invoice
                    Where
                        invoice.name = reference.reference_name
                ) As due_date,
                (
                    payment.name
                ) As payment_name,
                (
                    payment.posting_date
                ) As payment_date,
                (
                    payment.mode_of_payment
                ) As mode_of_payment,
                (
                    payment.party
                ) As customer_name,
                (
                    Select
                        customer.customer_group
                    From
                        `tabCustomer` As customer
                    Where
                        customer.name = payment.party
                ) As customer_group,
                (
                    Select
                        invoice.currency
                    From
                        `tabSales Invoice` As invoice
                    Where
                        invoice.name = reference.reference_name
                ) As invoice_currency,
                (
                    reference.total_amount
                ) As invoice_total_amount,
                (
                    reference.allocated_amount
                ) As invoice_allocated_amount,
                (
                    Select
                        invoice.outstanding_amount
                    From
                        `tabSales Invoice` As invoice
                    Where
                        invoice.name = reference.reference_name
                ) As invoice_outstanding_amount
            From
                `tabPayment Entry` payment
            Inner Join
                `tabPayment Entry Reference` reference
                On
                    reference.parent = payment.name
                    And reference.parenttype = "Payment Entry"
                    And reference.parentfield = "references"
            Where
                {conditions}
            Order By
                payment.posting_date Asc,
                reference.reference_name Asc
        """.format(conditions=conditions)


        return database.sql(query, values, as_dict=True)
    
    @classmethod
    def as_list(cls, values):
        array = list()

        for d in values:
            array.append(cls.to_list(d))
        
        return array

    @classmethod
    def to_list(cls, values):
        array = list()
        listorder = cls.fieldlist()

        for d in listorder:
            array.append(values[d])
        
        return array

    @staticmethod
    def fieldlist():
        return (
            "invoice_name",
            "invoice_date",
            "due_date",
            "payment_name",
            "payment_date",
            "mode_of_payment",
            "customer_name",
            "customer_group",
            "invoice_currency",
            "invoice_total_amount",
            "invoice_allocated_amount",
            "invoice_outstanding_amount",
        )

    @staticmethod
    def get_docfield(label, fieldtype="Data", options="", width=100):
        return "{label}:{fieldtype}/{options}:{width}" \
            .format(label=label, fieldtype=fieldtype, 
                    options=options, width=width)

    


def execute(filters):
    return QueryReport \
        .run(filters)