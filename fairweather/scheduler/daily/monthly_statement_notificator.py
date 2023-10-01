import frappe
from frappe.utils import cint


def runner():
    """This method is run by scheduler to send monthly statement to customers"""
    # execution plan
    # 1. load the Monthly Statement Configurator
    # 2. check for the send_on field (which is a list of days of the month)
    # 3. if today is the day of the month, then iterate over all the customers (customer_and_email of the same doctype)
    # 4. for each customer, "try" to create a new doctype of "Statement of Accounts" (which should automatically send the email at the moment of creation)
    # 5. if the new doctype being created does not have any records for the table "customer_and_email" then do not create the doctype (as it would send an empty statement and that just means the customer is up to date with their payments)

    # 1. load the Monthly Statement Configurator
    configurator = get_configurator()

    # 2. check for the send_on field (which is a list of days of the month)
    day_of_month = frappe.utils.get_datetime().day

    if day_of_month != cint(configurator.send_on):
        return "Not the day of the month to send the monthly statement"

    # 3. if today is the day of the month, then iterate over all the customers (customer_and_email of the same doctype)
    for customer_and_email in configurator.customer_and_email:
        doc = get_statement_of_accounts(
            customer_and_email.customer,
            customer_and_email.email,
            as_of_date=frappe.utils.today(),
        )

        doc.fetch_statement_of_accounts(throw=False)

        if not doc.statement_of_accounts:
            continue

        doc.save(ignore_permissions=True)


def get_statement_of_accounts(customer, email, as_of_date):
    """Returns a new Statement of Accounts document"""
    doc = frappe.get_doc(
        dict(
            doctype="Statement of Accounts",
            customer=customer,
            contact_email=email,
            as_of_date=as_of_date,
        )
    )

    return doc


def get_configurator():
    """Returns the Monthly Statement Configurator"""
    return frappe.get_single("Monthly Statement Configurator")