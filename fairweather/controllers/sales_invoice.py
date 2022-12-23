# -*- coding: utf-8 -*-
# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from functools import lru_cache
from frappe.utils import flt, cstr, cint

from fairweather.controllers.selling_common import add_taxes_if_needed


def validate(doc, method=None):
    fetch_discount_terms(doc)
    ensure_correct_value_of_avalara_state(doc)
    clear_state_and_tax_if_needed(doc)
    add_taxes_if_needed(doc)


def fetch_discount_terms(doc):
    from trupper.api import get_discount_terms

    if not doc.discount_terms_template:
        return False

    # this is flag
    if doc.get("dont_update_discount_schedule"):
        return False

    if not has_any_zero_discount(doc.discount_schedule):
        return False

    posting_date = doc.get("transaction_date") \
        or doc.get("posting_date")

    discount_terms = get_discount_terms(total=doc.total,
                                        terms_template=doc.discount_terms_template,
                                        posting_date=posting_date)

    discount_schedule = "discount_schedule"

    doc.set(discount_schedule, [])

    for discount_term in discount_terms:
        doc.append(discount_schedule, discount_term)


def has_any_zero_discount(discount_schedule=[]):
    for d in discount_schedule:
        if flt(d.discount_amount) == .000 \
                and flt(d.discount_rate):
            return True

    return False


def clear_state_and_tax_if_needed(doc):
    if not doc.request_not_to_add_taxes:
        return "Do NOT clear anything"

    # otherwise
    doc.avalara_state = None
    doc.avalara_tax_rate = None


@lru_cache()
def ensure_correct_value_of_avalara_state(doc):
    doctype = "Avalara Tax Rate"
    name = doc.avalara_tax_rate
    fieldname = "state"

    value = frappe.get_value(doctype, name, fieldname)
    doc.avalara_state = value
