# -*- coding: utf-8 -*-
# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from functools import lru_cache
from frappe.utils import flt, cstr, cint

from fairweather.controllers.exceptions import InvalidContactEmailConfigurationError
from fairweather.controllers.selling_common import (
    add_taxes_if_needed,
    get_primary_contact_email,
)



def validate(doc, method=None):
    ensure_correct_value_of_avalara_state(doc)
    ensure_correct_contact_email(doc)
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
    if not doc.avalara_tax_rate:
        doc.avalara_state = None  # ensure None if not Tax Rate
        return "No value for Avalara Tax Rate: Skipping."

    doctype = "Avalara Tax Rate"
    name = doc.avalara_tax_rate
    fieldname = "state"

    value = frappe.get_value(doctype, name, fieldname)
    doc.avalara_state = value


def ensure_correct_contact_email(doc):
    if not doc.contact_person:
        doc.contact_email = None
        return "No value for Contact Email: Skipping."

    try:
        doc.contact_email = get_primary_contact_email(for_contact=doc.contact_person, for_customer=doc.customer)
    except InvalidContactEmailConfigurationError as exc:
        doc.contact_email = None
        return exc.error_message
