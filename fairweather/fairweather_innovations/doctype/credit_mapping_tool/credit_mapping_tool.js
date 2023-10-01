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

            const query = "fairweather.queries.credit_mapping_tool.credit_note_for_mapping"
            const filters = {
                "customer": doc.customer,
                "docstatus": 1,
                "is_return": 1,
                // "outstanding_amount": ["=", 0],
            };

            return { query, filters };
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
            frm[field] = "";
            frm.refresh_field(field);
        }

        const number_fields = [
            "customer_balance",
            "unallocated_amount",
            "invoice_amount",
            "invoice_outstanding_amount",
        ];

        for (const field of number_fields) {
            frm[field] = .0;
            frm.refresh_field(field);
        }
    }

    function currency(num) {
        num = num.toString().replace(/\$|\,/g, '');
        if (isNaN(num)) {
            num = "0";
        }
    
        const sign = (num == (num = Math.abs(num)));
        num = Math.floor(num * 100 + 0.50000000001);
        let cents = num % 100;
        num = Math.floor(num / 100).toString();
    
        if (cents < 10) {
            cents = "0" + cents;
        }

        for (let index = 0; index < Math.floor((num.length - (1 + index)) / 3); index++) {
            num = num.substring(0, num.length - (4 * index + 3)) + ',' + num.substring(num.length - (4 * index + 3));
        }
    
        return (((sign) ? '' : '-') + '$' + num + '.' + cents);
    }

    function auto_set_amount_to_apply(frm) {
        const { doc } = frm;
        const { invoice_outstanding_amount, unallocated_amount } = doc;

        const amount_to_apply = Math.min(invoice_outstanding_amount, unallocated_amount);

        frm.set_value("amount_to_apply", amount_to_apply);

        if (amount_to_apply) {
            frappe.show_alert({
                message: __("Amount to Apply has been set to {0}", [currency(amount_to_apply)]),
                indicator: "green",
            });
        }
    }

    function fetch_customer_balance(frm) {
        const { doc } = frm;

        if (!doc.customer) {
            frappe.throw("Please select a customer first");
        }

        const method = "erpnext.accounts.utils.get_balance_on";
        const args = {
            "party_type": "Customer",
            "party": doc.customer,
        };

        const callback = function(response) {
            const { message: balance } = response;

            frm.set_value("customer_balance", flt(balance, 2));
        };

        frappe.call({ method, args, callback });
    }

    function fetch_unallocated_amount(frm) {
        const { doc } = frm;

        if (!doc.credit_note) {
            frm.set_value("unallocated_amount", 0.0);
            return "Please select a credit note first";
        }

        frappe.run_serially([
            _ => frappe.db.get_value("Sales Invoice", doc.credit_note, ["grand_total", "outstanding_amount"]),
            ({ message }) => {
                const {
                    grand_total,
                    outstanding_amount, 
                } = message;

                // credit note has a grand total in negative... lets make it positive
                const new_grand_total = - grand_total;
                const unallocated_amount = new_grand_total - outstanding_amount;

                frm.set_value("unallocated_amount", flt(unallocated_amount, 2));
            },
        ]);
    }

    // FIELDS EVENTS
    function customer(frm) {
        const { doc } = frm;

        if (!doc.customer) {
            clear_customer_dependent_fields(frm);
            return;
        }

        frappe.run_serially([
            _ => fetch_customer_balance(frm),
        ]);
    }

    function credit_note(frm) {
        frappe.run_serially([
            _ => fetch_unallocated_amount(frm),
        ]);
    }

    function unallocated_amount(frm) {
        frappe.run_serially([
            _ => auto_set_amount_to_apply(frm),
        ]);
    }

    function invoice_outstanding_amount(frm) {
        frappe.run_serially([
            _ => auto_set_amount_to_apply(frm),
        ]);
    }
    
    frappe.ui.form.on("Credit Mapping Tool", {
        refresh,
        customer,
        credit_note,
        unallocated_amount,
        invoice_outstanding_amount,
    });
}
