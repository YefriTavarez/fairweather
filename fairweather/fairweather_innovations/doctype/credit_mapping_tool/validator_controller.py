# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

"""Helper module to validate Credit Mapping Tool"""

from functools import lru_cache

import frappe
from frappe import _dict
from frappe.model.document import Document
from frappe.utils import cstr, flt

# hack! to be able to say frappe.as_dict
frappe.as_dict = _dict


class ValidatorController(Document):
    def validate(self):
        self.validate_customer()
        self.validate_credit_note()
        self.validate_sales_invoice()

    def validate_customer(self):
        """Validate the customer is the same for both documents"""
        if self.customer != self.get_credit_note().customer:
            frappe.throw("Customer in Credit Note is not the same")

        if self.customer != self.get_sales_invoice().customer:
            frappe.throw("Customer in Sales Invoice is not the same")

    def validate_credit_note(self):
        """
            1. Validate the credit note is not already applied to another invoice
            2. Validate the credit note is not already cancelled
            3. Validate the credit note is in deed a credit note
            4. Validate the amount to apply is not greater than the credit note
            5. Validate the credit note is not already applied to this invoice
        """
        self.validate_credit_note_is_not_applied_to_another_invoice()
        self.validate_credit_note_is_not_cancelled()
        self.validate_credit_note_is_a_credit_note()
        self.validate_amount_to_apply()
        self.validate_credit_note_is_not_applied_to_this_invoice()

    def validate_sales_invoice(self):
        """
            1. Validate the sales invoice is not already cancelled
            2. Validate the sales invoice is in deed a sales invoice
            3. Validate the amount to apply is not greater than the sales invoice
            4. Validate debit account against credit note is the same as the sales invoice
        """
        self.validate_sales_invoice_is_not_cancelled()
        self.validate_sales_invoice_is_not_a_credit_note()
        self.validate_amount_to_apply()
        self.validate_debit_account_against_credit_note_is_the_same_as_sales_invoice()

    def validate_amount_to_apply(self):
        """
            1. Validate the amount to apply is not greater than the credit note
            2. Validate the amount to apply is not greater than the sales invoice
        """
        self.validate_amount_to_apply_is_not_greater_than_credit_note()
        self.validate_amount_to_apply_is_not_greater_than_sales_invoice()

    def validate_credit_note_is_not_applied_to_another_invoice(self):
        """Validate the credit note is not already applied to another invoice"""
        credit_note = self.get_credit_note()

        doctype = self.doctype
        filters = {
            "credit_note": credit_note.name,
            "docstatus": 1,
            "name": ["!=", self.name],
        }

        fieldname = [
            "sum(amount_to_apply) as applied_amount",
            "group_concat(name) as credit_mapping_tools",
        ]

        values = frappe.db.get_value(
            doctype,
            filters,
            fieldname,
        )

        if not values:
            return  # backwards compatibility

        applied_amount, credit_mapping_tools = values

        if not applied_amount:
            return

        if flt(applied_amount) >= flt(abs(credit_note.grand_total), 2):
            frappe.throw(f"""
                <strong>Credit Note is already applied to another invoice</strong>
                <p>See Credit Mapping Tools:</p>
                <br>
                <p>{
                    frappe.utils.comma_and(
                        cstr(credit_mapping_tools).split(",")
                    )
                }</p>
            """)

    def validate_credit_note_is_not_cancelled(self):
        """Validate the credit note is not already cancelled"""
        credit_note = self.get_credit_note()

        if credit_note.docstatus == 2:
            frappe.throw("Credit Note is already cancelled")

    def validate_credit_note_is_a_credit_note(self):
        """Validate the credit note is in deed a credit note"""
        credit_note = self.get_credit_note()

        if not credit_note.is_return:
            frappe.throw("Credit Note is not a Credit Note")

    def validate_amount_to_apply_is_not_greater_than_credit_note(self):
        """Validate the amount to apply is not greater than the credit note"""
        credit_note = self.get_credit_note()

        if flt(self.amount_to_apply, 2) > flt(abs(credit_note.grand_total), 2):
            frappe.throw("Amount to apply is greater than Credit Note")

    def validate_amount_to_apply_is_not_greater_than_sales_invoice(self):
        """Validate the amount to apply is not greater than the sales invoice"""
        sales_invoice = self.get_sales_invoice()

        if flt(self.amount_to_apply, 2) > flt(sales_invoice.grand_total, 2):
            frappe.throw("Amount to apply is greater than Sales Invoice")

    def validate_credit_note_is_not_applied_to_this_invoice(self):
        """Validate the credit note is not already applied to this invoice"""
        credit_note = self.get_credit_note()
        sales_invoice = self.get_sales_invoice()

        doctype = self.doctype
        filters = {
            "credit_note": credit_note.name,
            "docstatus": 1,
            "sales_invoice": sales_invoice.name,
            "name": ["!=", self.name],
        }

        fieldname = "Sum(amount_to_apply) As applied_amount"

        applied_amount = frappe.db.get_value(
            doctype,
            filters,
            fieldname,
        )

        if flt(applied_amount, 2) >= flt(abs(credit_note.grand_total), 2):
            frappe.errprint(
                f"applied_amount: {applied_amount} >= {abs(credit_note.grand_total)}")
            frappe.throw("Credit Note is already applied to this invoice")

    def validate_sales_invoice_is_not_cancelled(self):
        """Validate the sales invoice is not already cancelled"""
        sales_invoice = self.get_sales_invoice()

        if sales_invoice.docstatus == 2:
            frappe.throw("Sales Invoice is already cancelled")

    def validate_sales_invoice_is_not_a_credit_note(self):
        """Validate the sales invoice is in deed a sales invoice"""
        sales_invoice = self.get_sales_invoice()

        if sales_invoice.is_return:
            frappe.throw("Sales Invoice is a Credit Note")

    def validate_debit_account_against_credit_note_is_the_same_as_sales_invoice(self):
        """Validate debit account against credit note is the same as the sales invoice"""
        credit_note = self.get_credit_note()
        sales_invoice = self.get_sales_invoice()

        if credit_note.debit_to != sales_invoice.debit_to:
            frappe.throw("Debit Account in Credit Note is not the same")
