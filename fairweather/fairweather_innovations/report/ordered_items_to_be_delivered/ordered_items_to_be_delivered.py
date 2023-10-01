# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import os
import frappe


def execute(filters=None):
    report = OrderedItemsToBeDelivered(filters)
    return report.run()


class OrderedItemsToBeDelivered():
    def __init__(self, filters):
        self.filters = filters
        self.initialize()

    def initialize(self):
        self.columns = list()
        self.data = list()

        self.filters.shipping_method = f"%{self.filters.shipping_method}%" if self.filters.shipping_method else "%"

    def run(self):
        self.setup_columns()
        self.setup_data()

        return self.columns, self.data

    def setup_columns(self):
        columns = list()

        columns.append({
            "label": "Sales Order",
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 120,
        })

        columns.append({
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120,
        })

        columns.append({
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 120,
        })

        columns.append({
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120,
        })

        columns.append({
            "label": "Customer Name",
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 150,
        })

        columns.append({
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
        })

        columns.append({
            "label": "Shipping Method",
            "fieldname": "shipping_method",
            "fieldtype": "Data",
            "width": 120,
        })

        columns.append({
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120,
        })

        columns.append({
            "label": "Ordered Qty",
            "fieldname": "ordered_qty",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Delivered Qty",
            "fieldname": "delivered_qty",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Qty to Deliver",
            "fieldname": "qty_to_deliver",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Amount to Deliver",
            "fieldname": "amount_to_deliver",
            "fieldtype": "Float",
            "width": 140,
        })

        columns.append({
            "label": "Available Qty",
            "fieldname": "available_qty",
            "fieldtype": "Float",
            "width": 120,
        })

        columns.append({
            "label": "Projected Qty",
            "fieldname": "projected_qty",
            "fieldtype": "Float",
            "width": 120,
        })

        columns.append({
            "label": "Item Delivery Date",
            "fieldname": "item_delivery_date",
            "fieldtype": "Date",
            "width": 120,
        })

        columns.append({
            "label": "Delay Days",
            "fieldname": "delay_days",
            "fieldtype": "Int",
            "width": 120,
        })

        columns.append({
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        })

        columns.append({
            "label": "Description",
            "fieldname": "description",
            "fieldtype": "Data",
            "width": 200,
        })

        columns.append({
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120,
        })

        columns.append({
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        })

        self.columns = columns

    def setup_data(self):
        query = self.get_query()
        values = self.filters

        for row in frappe.db.sql(query, values, as_dict=True):
            self.post_process(row)

    def post_process(self, row):
        # row["amount"] = row["ordered_qty"] * row["rate"]
        # row["amount_to_deliver"] = row["qty_to_deliver"] * row["rate"]

        self.data.append(row)

    def get_query(self):
        main_jql = self.get_main_jql()

        return frappe.render_template(main_jql, self.filters)

    def get_main_jql(self):
        """Will open the main jql file and return its content"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "ordered_items_to_be_delivered.jql"

        with open(os.path.join(current_dir, filename), "r") as file:
            return file.read()
