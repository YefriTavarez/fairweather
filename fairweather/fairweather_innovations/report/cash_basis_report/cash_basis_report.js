// Copyright (c) 2016, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

class QueryReport {
    constructor() {
        this.init();
        this.setup();
    }

    init() {
        this.filters = new Array();
    }

    onload() {
        // pass
    }

    setup() {
        this.setup_filters();
    }

    setup_filters() {
        const { filters, get_docfield } = this;
        const default_company = this.get_default_company();
        const default_start_date = this.get_default_start_date();
        const default_end_date = this.get_default_end_date();

        const fields = new Array(
            get_docfield("Company", "company", "Link", "Company", default_company, true),
            get_docfield("From Date", "from_date", "Date", null, default_start_date, true),
            get_docfield("To Date", "to_date", "Date", null, default_end_date, true),
            get_docfield("Customer Group", "customer_group", "Link", "Customer Group", null, false),
        );

        fields.map(docfield => {
            filters.push(docfield);
        });
    }

    get_docfield(label, fieldname, fieldtype, opts, defvalue, reqd) {
        return {
            label,
            fieldtype,
            fieldname,
            options: opts,
            default: defvalue,
            reqd
        };
    }

    get_default_company() {
        const {
            sys_defaults: {
                company
            }
        } = frappe;

        return company;
    }

    get_default_start_date() {
        const {
            datetime: {
                month_start,
            }
        } = frappe;

        return month_start();
    }

    get_default_end_date() {
        const {
            datetime: {
                month_end,
            }
        } = frappe;

        return month_end();
    }

}

frappe.query_reports["Cash Basis Report"] = new QueryReport();
