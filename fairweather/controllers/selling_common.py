# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

from functools import lru_cache

import frappe
from fairweather.controllers.exceptions import InvalidContactEmailConfigurationError


@frappe.whitelist()
def add_taxes_if_needed(doc):
    """
        Add taxes to a document if needed.
        :param doc: Document to add taxes to like a Sales Invoice.
    """

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

    doc.taxes = list()  # empty table

    fieldname = "taxes"
    for for_state in (True, False):
        tax_detail = get_tax_detail(doc, results, for_state)
        doc.append(fieldname, tax_detail)

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
            "location_description": f"County: {doc.county or doc.tax_region_name}\n",
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


def get_primary_contact_email(for_contact: str, for_customer: str) -> str:
    """
        Get the primary email for a contact
        :param for_contact: Contact to get the email for.
        :param for_customer: Customer to get the email for.
    
        :returns: Email address for the contact.
    """

    if not for_contact:
        raise InvalidContactEmailConfigurationError(
            error_code=1,
            error_message="No value for Contact: Skipping.",
        )

    if not for_customer:
        raise InvalidContactEmailConfigurationError(
            error_code=2,
            error_message="No value for Customer: Skipping.",
        )

    contact_email = _get_primary_contact_email(for_contact, for_customer)

    if not contact_email:
        raise InvalidContactEmailConfigurationError(
            error_code=3,
            error_message=f"No value for Contact Email for Customer: {for_customer} and Contact: {for_contact}",
        )

    return contact_email

def _get_primary_contact_email(for_contact: str, for_customer: str) -> str:
    """
        You shouldn't be using this function directly. Instead call get_primary_contact_email.
    """
    return frappe.get_value("Contact", [
        # ["Contact Email", "is_primary", "=", "1"],
        ["Contact", "name", "=", for_contact],
        ["Dynamic Link", "link_doctype", "=", "Customer"],
        ["Dynamic Link", "link_name", "=", for_customer],
    ], "`tabContact Email`.email_id")

    # return frappe.db.sql(
    #     """
    #         SELECT
    #             `tabContact Email`.email_id
    #         FROM
    #             `tabContact Email`
    #         INNER JOIN
    #             `tabContact`
    #         ON
    #             `tabContact Email`.parent = `tabContact`.name
    #         INNER JOIN
    #             `tabDynamic Link`
    #         ON
    #             `tabDynamic Link`.link_doctype = "Customer"
    #         AND `tabDynamic Link`.link_name = `tabContact`.customer
    #         WHERE
    #             `tabContact Email`.is_primary = 1
    #         AND `tabContact`.name = %s
    #     """)