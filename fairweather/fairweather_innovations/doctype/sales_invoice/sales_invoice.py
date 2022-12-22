# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from functools import lru_cache
from frappe.utils import flt, cstr, cint


def validate(doc, method=None):
	fetch_discount_terms(doc)
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

@frappe.whitelist()
def add_taxes_if_needed(doc):
	if doc.request_not_to_add_taxes:
		return "Requested NOT to add taxes: Do nothing for now"

	if not doc.avalara_tax_rate:
		return "No value for Avalara Tax Rate: Skip for now"

	results = get_tax_rates(doc.avalara_tax_rate)
	# results {	
	# 	"state": doc.state,
	# 	"state_account": get_account(doc.state),
	# 	"local_account": get_account(doc.state),
	# 	"state_rate": doc.state_rate,
	# 	"local_rate": doc.local_rate,
	# }

	doc.taxes = list()
	doc.append("taxes", get_tax_detail(doc, results, for_state=True))
	doc.append("taxes", get_tax_detail(doc, results, for_state=False))

	doc.calculate_taxes_and_totals()

	return doc


def get_tax_detail(doc, avalara_details, for_state=True):
	return {
		"account_currency": "USD",
		"account_head": avalara_details["state_account" if for_state else "local_account"],
		"base_tax_amount": 0.00,
		"base_tax_amount_after_discount_amount": 0.00,
		"base_total": 0.0000,
		"charge_type": "On Net Total",
		"cost_center": doc.cost_center,
		"description": avalara_details["state_description" if for_state else "location_description"],
		"dont_recompute_tax": 0,
		"included_in_paid_amount": 0,
		"included_in_print_rate": 0,
		"rate": avalara_details["state_rate" if for_state else "local_rate"],
		"tax_amount": 0.00,
		"tax_amount_after_discount_amount": 0.00,
		"total": 0.0000,
	}

@frappe.whitelist()
def get_tax_rates(tax_rate):
	doctype = "Avalara Tax Rate"
	name = tax_rate

	try:
		doc = frappe.get_doc(doctype, name)
	except frappe.DoesNotExist:
		frappe.throw(f"Tax Rate with ID {name} was not found")
	else:
		# explict return
		return {
			"state": doc.state,
			"state_account": get_account(doc.state).state_account,
			"local_account": get_account(doc.state).local_account,
			"state_rate": doc.state_rate,
			"state_description": f"State: {doc.state}",
			"location_description": f"Location: {doc.tax_region_name}\nZipCode: {doc.zip_code}",
			"local_rate": doc.estimated_county_rate or doc.estimated_city_rate or doc.estimated_special_rate,
		}


@lru_cache()
def get_account(state):
	doctype = "Avalara State"
	name = state

	doc = frappe.get_doc(doctype, name)

	return frappe._dict(
		state_account=doc.state_account,
		local_account=doc.local_account,
	)
