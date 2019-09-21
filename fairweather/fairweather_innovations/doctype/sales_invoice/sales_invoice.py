# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, cstr, cint

def validate(doc, method):
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
