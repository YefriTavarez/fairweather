# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

from typing import Generator, List

import frappe
from frappe.model.document import Document


class MonthlyStatementConfigurator(Document):
    def validate(self):
        self.allow_multiple_fetches = False

    @property
    def customers(self):
        return {(d.customer, d.email) for d in self.customer_and_email}

    @frappe.whitelist()
    def fetch_customers(self):
        """Fetches all customers from the system"""
        filters = self.get_filters()
        customer_list = self.get_customers(filters)

        self.validate_maximum_fetches(customer_list)
        self.clear_customer_table_if_applies()
        self.add_customers_to_table(customer_list)
        self.sort_customer_table()
        self.notify_user_of_missing_emails()

    @frappe.whitelist()
    def remove_customers_without_email(self):
        """Removes all customers that don't have an email"""
        self.customer_and_email = [
            frappe.copy_doc(d) for d in self.customer_and_email if d.email
        ]

        # update idx
        for idx, d in enumerate(self.customer_and_email, start=1):
            d.idx = idx

    def get_current_search(self):
        """Based on the given filters return a pretty string to show in the search field"""
        search = list()

        if self.price_list:
            search += [f"Price List: {self.price_list}"]

        if self.customer_group:
            search += [f"Customer Group: {self.customer_group}"]

        if self.payment_terms:
            search += [f"Terms: {self.payment_terms}"]

        if self.account:
            search += [f"Account: {self.account}"]

        return ", ".join(search) or "No Search Criteria"

    def get_email(self, for_customer):
        """Returns the email for the given customer"""
        # Two posibilities:
        # 	1. The customer has a contact with the email
        # 	2. The customer has an address with the email (Billing Address first)

        email = self.get_email_from_contact(for_customer)

        if not email:
            email = self.get_email_from_address(for_customer, billing_first=True)

        if not email:
            email = self.get_email_from_address(for_customer)

        if not email:
            self.report_missing_email(for_customer)

        return email

    def get_email_from_contact(self, for_customer):
        """Returns the email from the contact for the given customer"""
        doctype = "Contact"

        pluck = "email_id"

        filters = [
            ["Dynamic Link", "link_doctype", "=", "Customer"],
            ["Dynamic Link", "link_name", "=", for_customer],
        ]

        # the customer might have more than one contact.
        email_list = frappe.get_list(
            doctype, filters, pluck=pluck
        )

        if email_list and email_list[0] is not None:
            # take the first contact email and split it by comma...
            # some contacts have more than one email... not sure why!
            emails = email_list[0].split(",")
            email =  emails[0].strip()

            if email:
                return email

        return None

    def get_email_from_address(self, for_customer, billing_first=False):
        """Returns the email from the address for the given customer"""
        doctype = "Address"

        pluck = "email_id"

        filters = [
            ["Dynamic Link", "link_doctype", "=", "Customer"],
            ["Dynamic Link", "link_name", "=", for_customer],
        ]

        or_filters = [
            ["Address", "is_primary_address", "=", 1],
            ["Address", "address_type", "=", "Billing"],
        ]

        if not billing_first:
            filters = [
                ["Dynamic Link", "link_doctype", "=", "Customer"],
                ["Dynamic Link", "link_name", "=", for_customer],
            ]

        email_list = frappe.get_list(
            doctype, filters=filters, or_filters=or_filters, pluck=pluck
        )

        if email_list:
            email = email_list[0]

            if email:
                return email

        return None

    def get_customers(self, filters):
        doctype = "Customer"
        pluck = "name"
        order_by = "name"

        return frappe.get_list(
            doctype, filters, pluck=pluck, order_by=order_by
        )

    def report_missing_email(self, customer):
        """Will remember a list of customers that don't have an email"""
        if not hasattr(self, "missing_emails"):
            self.missing_emails = list()

        self.missing_emails.append(customer)

    def get_missing_emails(self):
        """Returns a list of customers that don't have an email"""
        if not hasattr(self, "missing_emails"):
            return list()

        return self.missing_emails

    def notify_user_of_missing_emails(self):
        if missing_emails := self.get_missing_emails():
            frappe.msgprint(
                f"""Couldn't find an email for the following customers:
                <br>
                <ul>
                    {"".join([f"<li>{customer}</li>" for customer in missing_emails])}
                </ul>
                """
            )

    def sort_customer_table(self):
        """Sorts the customer table by customer name"""
        self.customer_and_email = sorted(
            self.customer_and_email, key=lambda d: d.customer
        )

        # update idx
        for idx, d in enumerate(self.customer_and_email, start=1):
            d.idx = idx

    def add_customers_to_table(self, customer_list):
        for customer in customer_list:
            email = self.get_email(for_customer=customer)

            if (customer, email) in self.customers:
                continue

            search = self.get_current_search()

            self.append("customer_and_email", {
                "customer": customer,
                "email": email,
                "search": search,
            })

    def clear_customer_table_if_applies(self):
        if not self.allow_multiple_fetches:
            self.customer_and_email = list()

    def validate_maximum_fetches(self, customer_list):
        customer_count = len(customer_list)

        if customer_count and customer_count > 1_000:
            frappe.throw(
                f"Too many customers found ({customer_count}). Please, narrow your search criteria."
            )

    def get_filters(self):
        filters = list()

        if self.price_list:
            filters.append(["Customer", "price_list", "=", self.price_list])

        if self.customer_group:
            filters.append(["Customer", "customer_group", "=", self.customer_group])

        if self.payment_terms:
            filters.append(["Customer", "payment_terms", "=", self.payment_terms])

        if self.account:
            filters.append(["Party Account", "account", "=", self.account])

        return filters

    price_list: str = None
    customer_group: str = None
    payment_terms: str = None
    account: str = None
    allow_multiple_fetches: bool = False
    customer_and_email: List[Document] = list() 
