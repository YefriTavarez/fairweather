// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

"use strict"

frappe.ui.form.on("Customer", {
	refresh(frm) {
		frappe.run_serially([
			_ => frm.trigger("add_custom_buttons"),
		]);
	},
	onload_post_render(frm) {
        frappe.run_serially([
            _ => frm.trigger("setup_html_template"),
        ]);
	},
	add_custom_buttons(frm) {
		if (frm.is_new()) {
			// skip
		} else {
			frm.trigger("add_customer_statement_button");
		}
	},
	add_customer_statement_button(frm) {
		const label = __("Statement of Accounts");
		const action = () => {
			frm.trigger("show_customer_statement");
		};

		const btn = frm.add_custom_button(label, action);
		btn.removeClass("btn-default");
		btn.addClass("btn-success");
		btn.html(`
			<span>${label}</span>
			<svg class="icon ml-2 icon-xs" style="stroke: white">
				<use class="" href="#icon-arrow-up-right"></use>
			</svg>
		`);
	},
	setup_html_template(frm) {
        const { doc } = frm;

        const { 
            doc: {
                __onload: {
                    __statement_of_accounts: template
                }
            }
        } = frm;

        frappe.templates["statement_of_accounts"] = template;
	},
	show_customer_statement(frm) {
		const { doc, events } = frm;
        const { __onload: server_data } = doc;

		const storage = new fairweather.LocalStorage(
			"fairweather.statement_of_accounts"
		);

		const dialog = frappe.prompt([
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": (_ => {
					const fieldname = "from_date";
					const fallback = frappe.datetime.year_start();
					return storage.getValue(fieldname, fallback);
				})(),
				"reqd": 0,
				"change": function() {
					storage.setValue("from_date", this.value);
				}
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": (_ => {
					const fieldname = "to_date";
					const fallback = frappe.datetime.get_today();
					return storage.getValue(fieldname, fallback);
				})(),
				"reqd": 1,
				"change": function() {
					storage.setValue("to_date", this.value);
				}
			},
		], ({ from_date, to_date }) => {
			const { name } = doc;
            // const { __statement_of_accounts: template } = server_data;
            const template = "statement_of_accounts";
			events.get_report_data({ frm, template, from_date, to_date, name });
		}, __("Select Dates"), __("Print"));
        
		dialog.set_secondary_action(_ => {
			const { name } = doc;
			const { from_date, to_date } = dialog.get_values();

			frappe.route_options = {
                "customer": name,
				"from_date": from_date,
				"to_date": to_date,
			};
            
			frappe.set_route("query-report", "Statement of Accounts");
		}).html(`${__("View Report")}`);
	},
	get_report_data({frm, template, from_date, to_date, name: customer}) {
        const { events } = frm;
        
        const method = "frappe.desk.query_report.run";
        const company = frappe.defaults.get_default("Company");
        const args = {
            filters: {
                company,
                customer,
                from_date,
                to_date,
            },
            report_name: "Statement of Accounts",
        };


        frappe.call(method, args)
            .then(data => {
                const { message: { result } } = data;

                if (!result || !result.length) {
                    frappe.msgprint(__("No data found"));
                    return;
                }

                events.printit({
                    frm,
                    template,
                    from_date,
                    to_date,
                    data: result,
                    name: customer 
                });
            });
    },
	printit({frm, template, from_date, to_date, name, data }) {
        const filters = {
            "customer": name,
            "from_date": from_date,
            "to_date": to_date,
        };

        const print_settings = {
            "columns": [
                {
                    "fieldname": "posting_date",
                    "label": __("Posting Date"),
                    "fieldtype": "Date",
                    "width": "100px"
                },
                {
                    "fieldname": "name",
                    "label": __("Invoice"),
                    "fieldtype": "Link",
                    "options": "Sales Invoice",
                    "width": "100px"
                },
                {
                    "fieldname": "grand_total",
                    "label": __("Amount"),
                    "fieldtype": "Currency",
                    "width": "100px"
                },
                {
                    "fieldname": "due_date",
                    "label": __("Due Date"),
                    "fieldtype": "Date",
                    "width": "100px"
                },
                {
                    "fieldname": "outstanding_amount",
                    "label": __("Outstanding Amount"),
                    "fieldtype": "Currency",
                    "width": "100px"
                },
            ],
            template: template,
        }

	
		// this.make_access_log("Print", "PDF");
		frappe.render_grid({
			template: template,
			title: __("Statement of Accounts"),
			subtitle: null,
			print_settings: print_settings,
			landscape: false,
			filters: filters,
			data: data,
			columns: print_settings.columns,
			original_data: testData,
			report: null,
		});
	}
});


var testData = [
    {
        "posting_date": "2022-10-13",
        "name": "SINV-13845",
        "grand_total": 171.39,
        "due_date": "2023-01-11",
        "outstanding_amount": 171.39,
        "_index": 0
    },
    {
        "posting_date": "2022-10-17",
        "name": "SINV-13870",
        "grand_total": 251.95,
        "due_date": "2023-01-15",
        "outstanding_amount": 251.95,
        "_index": 1
    },
    {
        "posting_date": "2022-10-25",
        "name": "SINV-13944",
        "grand_total": 73.5,
        "due_date": "2023-01-23",
        "outstanding_amount": 73.5,
        "_index": 2
    },
    {
        "posting_date": "2022-10-26",
        "name": "SINV-13955",
        "grand_total": 3067.99,
        "due_date": "2023-01-24",
        "outstanding_amount": 3067.99,
        "_index": 3
    },
    {
        "posting_date": "2022-10-26",
        "name": "SINV-13956",
        "grand_total": 4243.35,
        "due_date": "2023-01-24",
        "outstanding_amount": 4243.35,
        "_index": 4
    },
    {
        "posting_date": "2022-10-31",
        "name": "SINV-13988",
        "grand_total": 1324.33,
        "due_date": "2023-01-29",
        "outstanding_amount": 1324.33,
        "_index": 5
    },
    {
        "posting_date": "2022-10-31",
        "name": "SINV-13989",
        "grand_total": 1431.51,
        "due_date": "2023-01-29",
        "outstanding_amount": 1431.51,
        "_index": 6
    },
    {
        "posting_date": "2022-11-04",
        "name": "SINV-14019",
        "grand_total": 361.74,
        "due_date": "2023-02-02",
        "outstanding_amount": 361.74,
        "_index": 7
    },
    {
        "posting_date": "2022-11-14",
        "name": "SINV-14073",
        "grand_total": 518.17,
        "due_date": "2023-02-12",
        "outstanding_amount": 518.17,
        "_index": 8
    },
    {
        "posting_date": "2022-11-15",
        "name": "SINV-14087",
        "grand_total": 1026.86,
        "due_date": "2023-02-13",
        "outstanding_amount": 1026.86,
        "_index": 9
    },
    {
        "posting_date": "2022-11-15",
        "name": "SINV-14088",
        "grand_total": 1345.38,
        "due_date": "2023-02-13",
        "outstanding_amount": 1345.38,
        "_index": 10
    },
    {
        "posting_date": "2022-11-17",
        "name": "SINV-14118",
        "grand_total": 181.76,
        "due_date": "2023-02-15",
        "outstanding_amount": 181.76,
        "_index": 11
    },
    {
        "posting_date": "2022-11-23",
        "name": "SINV-14152",
        "grand_total": 1033.33,
        "due_date": "2023-02-21",
        "outstanding_amount": 1033.33,
        "_index": 12
    },
    {
        "posting_date": "2022-11-23",
        "name": "SINV-14153",
        "grand_total": 511.81,
        "due_date": "2023-02-21",
        "outstanding_amount": 511.81,
        "_index": 13
    },
    {
        "posting_date": "2022-12-02",
        "name": "SINV-14227",
        "grand_total": 211.55,
        "due_date": "2023-03-02",
        "outstanding_amount": 211.55,
        "_index": 14
    },
    {
        "posting_date": "2022-12-06",
        "name": "SINV-14243",
        "grand_total": 52.23,
        "due_date": "2023-03-06",
        "outstanding_amount": 52.23,
        "_index": 15
    },
    {
        "posting_date": "2022-12-07",
        "name": "SINV-14255",
        "grand_total": 1207.63,
        "due_date": "2023-03-07",
        "outstanding_amount": 1207.63,
        "_index": 16
    },
    {
        "posting_date": "2022-12-07",
        "name": "SINV-14256",
        "grand_total": 1804.18,
        "due_date": "2023-03-07",
        "outstanding_amount": 1804.18,
        "_index": 17
    },
    {
        "posting_date": "2022-12-09",
        "name": "SINV-14300",
        "grand_total": 561.01,
        "due_date": "2023-03-09",
        "outstanding_amount": 561.01,
        "_index": 18
    },
    {
        "posting_date": "2022-12-12",
        "name": "SINV-14323",
        "grand_total": 110.25,
        "due_date": "2023-03-12",
        "outstanding_amount": 110.25,
        "_index": 19
    },
    {
        "posting_date": "2022-12-12",
        "name": "SINV-14324",
        "grand_total": 76.44,
        "due_date": "2023-03-12",
        "outstanding_amount": 76.44,
        "_index": 20
    },
    {
        "posting_date": "2022-12-14",
        "name": "SINV-14359",
        "grand_total": 303.19,
        "due_date": "2023-03-14",
        "outstanding_amount": 303.19,
        "_index": 21
    },
    {
        "posting_date": "2022-12-14",
        "name": "SINV-14360",
        "grand_total": 215.87,
        "due_date": "2023-03-14",
        "outstanding_amount": 215.87,
        "_index": 22
    },
    {
        "posting_date": "2022-12-16",
        "name": "SINV-14379",
        "grand_total": 357.21,
        "due_date": "2023-03-16",
        "outstanding_amount": 357.21,
        "_index": 23
    },
    {
        "posting_date": "2022-12-16",
        "name": "SINV-14380",
        "grand_total": 75,
        "due_date": "2023-03-16",
        "outstanding_amount": 75,
        "_index": 24
    },
    {
        "posting_date": "2023-01-03",
        "name": "SINV-14458",
        "grand_total": 159.26,
        "due_date": "2023-04-03",
        "outstanding_amount": 159.26,
        "_index": 25
    },
    {
        "posting_date": "2023-01-06",
        "name": "SINV-14485",
        "grand_total": 3297.42,
        "due_date": "2023-04-06",
        "outstanding_amount": 3297.42,
        "_index": 26
    },
    {
        "posting_date": "2023-01-06",
        "name": "SINV-14486",
        "grand_total": 7269.79,
        "due_date": "2023-04-06",
        "outstanding_amount": 7269.79,
        "_index": 27
    },
    {
        "_rowIndex": "",
        "is_total_row": true,
        "posting_date": null,
        "name": null,
        "grand_total": 31244.09999999999,
        "due_date": null,
        "outstanding_amount": 31244.09999999999
    }
]
