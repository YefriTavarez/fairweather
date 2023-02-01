// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt

{
    // FORM EVENTS
    function refresh(frm) {
        frappe.run_serially([
            _ => set_queries(frm),
        ]);
    }

    // HELPER METHODS
    function set_queries(frm) {
        frappe.run_serially([
            _ => set_customer_query(frm),
            _ => set_credit_note_query(frm),
            _ => set_sales_invoice_query(frm),
        ]);
    }

    function set_customer_query(frm) {
        const fieldname = "customer";
        const get_query = function() {
            const query = "fairweather.queries.credit_mapping_tool.customer_query";
            const filters = {};

            clear_customer_dependent_fields(frm);

            return { query, filters };
        };

        frm.set_query(fieldname, get_query);
    }

    function set_credit_note_query(frm) {
        const fieldname = "credit_note";
        const get_query = function() {
            const { doc } = frm;
            if (!doc.customer) {
                frappe.throw("Please select a customer first");
            }

            const filters = {
                "customer": doc.customer,
                "docstatus": 1,
                "is_return": 1,
                "outstanding_amount": [">", 0],
            };

            return { filters };
        };

        frm.set_query(fieldname, get_query);
    }

    function set_sales_invoice_query(frm) {
        const fieldname = "sales_invoice";
        const get_query = function() {
            const { doc } = frm;
            if (!doc.customer) {
                frappe.throw("Please select a customer first");
            }

            const filters = {
                "customer": doc.customer,
                "docstatus": 1,
                "is_return": 0,
                "outstanding_amount": [">", 0],
            };

            return { filters };
        };

        frm.set_query(fieldname, get_query);
    }

    function clear_customer_dependent_fields(frm) {
        const data_fields = [
            "credit_note",
            "sales_invoice",
        ];

        for (const field of data_fields) {
            frm.set_value(field, "");
        }

        const number_fields = [
            "customer_balance",
            "unallocated_amount",
            "invoice_amount",
            "invoice_outstanding_amount",
        ];

        for (const field of number_fields) {
            frm.set_value(field, .0);
        }
    }

    function auto_set_amount_to_apply(frm) {
        const { doc } = frm;
        const { invoice_outstanding_amount, unallocated_amount } = doc;

        const amount_to_apply = Math.min(invoice_outstanding_amount, unallocated_amount);

        frm.set_value("amount_to_apply", amount_to_apply);
    }

    function fetch_customer_balance(frm) {
        const { doc } = frm;
        const { customer } = doc;

        if (!customer) {
            frappe.throw("Please select a customer first");
        }

        const method = "erpnext.accounts.utils.get_balance_on";
        const args = {
            "party_type": "Customer",
            "party": customer,
        };

        const callback = function(response) {
            const { message: balance } = response;

            frm.set_value("customer_balance", flt(balance, 2));
        };

        frappe.call({ method, args, callback });
    }

    // FIELDS EVENTS
    function customer(frm) {
        const { doc } = frm;
        const { customer } = doc;

        if (!customer) {
            return;
        }

        frappe.run_serially([
            _ => fetch_customer_balance(frm),
        ]);
    }

    function unallocated_amount(frm) {
        const { doc } = frm;

        if (
            !doc.unallocated_amount
            || !doc.invoice_outstanding_amount
        ) {
            return;
        }

        frappe.run_serially([
            _ => auto_set_amount_to_apply(frm),
        ]);
    }

    function invoice_outstanding_amount(frm) {
        const { doc } = frm;

        if (
            !doc.unallocated_amount
            || !doc.invoice_outstanding_amount
        ) {
            return;
        }

        frappe.run_serially([
            _ => auto_set_amount_to_apply(frm),
        ]);
    }
    
    frappe.ui.form.on("Credit Mapping Tool", {
        refresh,
        customer,
        unallocated_amount,
        invoice_outstanding_amount,
    });
}
