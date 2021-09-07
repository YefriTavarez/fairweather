# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, money_in_words

from erpnext.accounts.utils import get_balance_on
from erpnext.accounts.party import get_party_account
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.doctype.account.account import get_account_currency

def get_journal_entry(credit_note, sales_invoice, mapping_tool):
    doctype = "Journal Entry"
    doc = frappe.new_doc(doctype)

    for account in get_accounts(credit_note, sales_invoice, mapping_tool):
        doc.append("accounts", account)

    doc.update({
        "write_off_amount": 0,
        "naming_series": "MAP-TOOL-",
        "voucher_type": "Journal Entry",
        "total_amount_currency": total_amount_currency(credit_note, sales_invoice),
        # "letter_head": "SEAVIEW LETTER HEAD",
        "title": get_customer(credit_note, sales_invoice),
        "total_amount_in_words": get_total_amount_in_words(credit_note, sales_invoice, mapping_tool),
        "multi_currency": 0,
        "company": get_company(credit_note, sales_invoice),
        "total_credit": get_credit(mapping_tool),
        "difference": 0,
        "pay_to_recd_from": get_customer(credit_note, sales_invoice),
        "total_amount": get_credit(mapping_tool) + get_debit(mapping_tool),
        "remark": get_remarks(sales_invoice, credit_note, mapping_tool),
        "write_off_based_on": "Accounts Receivable",
        "total_debit": get_debit(mapping_tool),
        "is_opening": "No",
        "posting_date": frappe.utils.today(),
    })

    return doc


def get_remarks(sales_invoice, credit_note, mapping_tool):
    remarks_template = "$ {amount_to_apply} against Sales Invoice " \
        "{sales_invoice} taken from Credit Note {credit_note}"

    kwargs = {
        "sales_invoice": sales_invoice.name,
        "credit_note": credit_note.name,
        "amount_to_apply": mapping_tool.amount_to_apply,
    }

    return remarks_template.format(**kwargs)

def get_account_balance(doc):
    account = doc.debit_to

    return get_balance_on(account=account)

def get_company(credit_note, sales_invoice):
    credit_note_company = credit_note.company
    sales_invoice_company = sales_invoice.company

    if not credit_note_company == sales_invoice_company:
        frappe.throw("Company should be the same for both transactions")

    return sales_invoice_company


def get_total_amount(mapping_tool):
    return get_credit(mapping_tool) \
        + get_debit(mapping_tool)

def get_customer(credit_note, sales_invoice):
    credit_note_customer = credit_note.customer
    sales_invoice_customer = sales_invoice.customer

    if not credit_note_customer == sales_invoice_customer:
        frappe.throw("Customer should be the same for both transactions")

    return sales_invoice_customer


def get_credit_in_account_currency(mapping_tool):
    return get_credit(mapping_tool)


def get_debit_in_account_currency(mapping_tool):
    return get_debit(mapping_tool)


def get_credit(doc, precision=6):
    return flt(doc.amount_to_apply, precision)

def get_debit(doc, precision=6):
    return flt(doc.amount_to_apply, precision)


def get_party_balance(credit_note, sales_invoice):
    credit_note_customer = credit_note.customer
    sales_invoice_customer = sales_invoice.customer

    credit_note_company = credit_note.company
    sales_invoice_company = sales_invoice.company

    if not credit_note_company == sales_invoice_company:
        frappe.throw("Company should be the same for both transactions")

    if not credit_note_customer == sales_invoice_customer:
        frappe.throw("Customer should be the same for both transactions")

    party_type = "Customer"
    party = sales_invoice_customer
    company = sales_invoice_company

    return get_balance_on(party_type=party_type, party=party, company=company)

def get_recv_account(doc):
    party_type = "Customer"
    party = doc.customer
    company = doc.company

    return get_party_account(party_type, party, company)

def get_total_amount_in_words(credit_note, sales_invoice, mapping_tool):
    total_amount = get_total_amount(mapping_tool)
    currency = total_amount_currency(credit_note, sales_invoice)

    return money_in_words(total_amount, main_currency=currency, fraction_currency="Cents")

def total_amount_currency(credit_note, sales_invoice):
    credit_note_currency = credit_note.currency
    sales_invoice_currency = sales_invoice.currency

    if not credit_note_currency == sales_invoice_currency:
        frappe.throw("Currency should be the same for both transactions")

    return sales_invoice_currency

def get_accounts(credit_note, sales_invoice, mapping_tool):
    return [
        {
            # "exchange_rate": get_exchange_rate(credit_note, sales_invoice),
            "exchange_rate": 1,
            "party_type": "Customer",
            "reference_type": "Sales Invoice",
            "debit": get_debit(mapping_tool),
            "party": get_customer(credit_note, sales_invoice),
            "against_account": get_customer(credit_note, sales_invoice),
            "account_type": "Receivable",
            "reference_name": credit_note.name,
            "debit_in_account_currency": get_debit_in_account_currency(mapping_tool),
            "party_balance": get_party_balance(credit_note, sales_invoice),
            "is_advance": "No",
            "account_currency": "USD",
            "account": get_recv_account(credit_note),
            "credit": 0,
            "parenttype": "Journal Entry",
            "balance": get_account_balance(credit_note),
            "credit_in_account_currency": 0,
        },
        {
            "exchange_rate": 1,
            "party_type": "Customer",
            "reference_type": "Sales Invoice",
            "debit": 0,
            "party": get_customer(credit_note, sales_invoice),
            "against_account": get_customer(credit_note, sales_invoice),
            "account_type": "Receivable",
            "reference_name": sales_invoice.name,
            "debit_in_account_currency": 0,
            "party_balance": get_party_balance(credit_note, sales_invoice),
            "is_advance": "No",
            "account_currency": "USD",
            "account": get_recv_account(sales_invoice),
            "credit": get_credit(mapping_tool),
            "parenttype": "Journal Entry",
            "balance": get_account_balance(sales_invoice),
            "credit_in_account_currency": get_credit_in_account_currency(mapping_tool),
        },
    ]