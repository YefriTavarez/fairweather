# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

from functools import lru_cache

import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries

from .validator_controller import ValidatorController


class CreditMappingTool(ValidatorController):
    def on_submit(self):
        self.map_credit(cancel=False)

    def on_cancel(self):
        title = "Not implemented yet"
        message = """
            <p>This feature is not implemented yet.</p>
            <p>If you need this feature, please contact the developer.</p>
            """
        frappe.throw(message, title=title)
        # self.map_credit(cancel=True)

    def map_credit(self, cancel=False):
        customer = self.get_customer()

        credit_note = self.get_credit_note()
        sales_invoice = self.get_sales_invoice()

        cr_entry = self.get_general_entry(
            posting_date=self.posting_date,
            due_date=credit_note.due_date or sales_invoice.due_date,
            account=self.get_receivable_account(),
            credit=self.amount_to_apply,
            party=customer,
            cost_center=None,
            credit_in_account_currency=self.amount_to_apply,
            against_voucher=sales_invoice.name,
            voucher_no=credit_note.name,
            remarks=self.get_remarks(for_cancel=cancel),
            fiscal_year=self.get_applicable_fiscal_year(),
        )

        si_entry = self.get_general_entry(
            posting_date=self.posting_date,
            due_date=sales_invoice.due_date,
            account=self.get_receivable_account(),
            debit=self.amount_to_apply,
            party=customer,
            cost_center=None,
            debit_in_account_currency=self.amount_to_apply,
            against_voucher=credit_note.name,
            voucher_no=sales_invoice.name,
            remarks=self.get_remarks(for_cancel=cancel),
            fiscal_year=self.get_applicable_fiscal_year(),
        )

        gl_entries = [cr_entry, si_entry]
        # if cancel:
        #     make_reverse_gl_entries(gl_entries)
        # else:
        #    make_gl_entries(gl_entries)
        make_gl_entries(gl_entries, cancel=cancel)

    def get_customer(self, throw=True) -> str:
        if not self.customer and throw:
            frappe.throw("Customer is required")

        return self.customer

    def get_credit_note(self, throw=True) -> SalesInvoice:
        if not self.credit_note and throw:
            frappe.throw("Credit Note is required")

        @lru_cache(maxsize=128)
        def _credit_note(name):
            doctype = "Sales Invoice"
            return frappe.get_doc(doctype, name)

        return _credit_note(self.credit_note)

    def get_sales_invoice(self, throw=True) -> SalesInvoice:
        if not self.sales_invoice and throw:
            frappe.throw("Sales Invoice is required")

        @lru_cache(maxsize=128)
        def _sales_invoice(name):
            doctype = "Sales Invoice"
            return frappe.get_doc(doctype, name)

        return _sales_invoice(self.sales_invoice)

    def get_applicable_fiscal_year(self, throw=True) -> str:
        """
            Load the fiscal year from the latest document.
            If Sales Invoice is newer, use that fiscal year.
            If Credit Note is newer, use that fiscal year.
        """
        credit_note = self.get_credit_note()
        sales_invoice = self.get_sales_invoice()

        date = credit_note.posting_date
        if sales_invoice.posting_date > date:
            date = sales_invoice.posting_date

        return self.get_fiscal_year(date)

    @lru_cache(maxsize=128)
    def get_fiscal_year(self, date) -> str:
        """
            Get the fiscal year from the given date.
        """
        if not date:
            frappe.throw("Date is required")

        doctype = "Fiscal Year"
        filters = {
            "year_start_date": ["<=", date],
            "year_end_date": [">=", date],
        }

        return frappe.db.get_value(doctype, filters)

    def get_remarks(self, for_cancel) -> str:
        remarks = f"""Balance applied to Sales Invoice 
#{self.sales_invoice} from Credit Note #{self.credit_note}"""

        if for_cancel:
            remarks = f"""Balance unapplied from Sales Invoice
#{self.sales_invoice} from Credit Note #{self.credit_note}"""

        return remarks

    def get_receivable_account(self, throw=True) -> str:
        """
            Get the receivable account from the customer.
        """
        credit_note = self.get_credit_note()
        sales_invoice = self.get_sales_invoice()

        receivable_account = credit_note.debit_to
        if sales_invoice.debit_to != receivable_account and throw:
            frappe.throw(f"""
                Debit To Accounts are not the same for:
                <strong>Credit Note</strong> #{credit_note.name}
                and <strong>Sales Invoice</strong> #{sales_invoice.name}
            """)

        return receivable_account

    def get_general_entry(
        self,
        posting_date,
        due_date,
        account,
        party,
        cost_center,
        against_voucher,
        voucher_no,
        remarks,
        fiscal_year,
        debit=0,
        credit=0,
        debit_in_account_currency=0,
        credit_in_account_currency=0,
    ) -> dict:
        gl = frappe.as_dict({
            "posting_date": posting_date,
            "due_date": due_date,
            "account": account,
            "debit": debit,
            "credit": credit,
            "party": party,
            "cost_center": None,
            "debit_in_account_currency": debit_in_account_currency,
            "credit_in_account_currency": credit_in_account_currency,
            "voucher_no": voucher_no,
            "voucher_type": "Sales Invoice",
            "against_voucher": against_voucher,
            "remarks": remarks,
            "fiscal_year": fiscal_year,
            "company": frappe.defaults.get_user_default("Company"),
            "account_currency": "USD",
            "against_voucher_type": "Sales Invoice",
            "party_type": "Customer",
            "is_opening": "No",
            "is_advance": "No",
            "to_rename": 1,
        })

        return gl
