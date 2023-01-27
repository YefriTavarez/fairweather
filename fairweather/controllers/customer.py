# -*- coding: utf-8 -*-
# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from functools import lru_cache


def onload(self, method):
    self.set_onload(
        "__statement_of_accounts",
        get_statement_of_accounts_html(),
    )


def get_statement_of_accounts_html():
    app_name = "fairweather"
    app_path = frappe.get_app_path(app_name)

    template_path = f"{app_path}/templates/includes/statement_of_accounts.html"
    with open(template_path) as template_file:
        return template_file.read()
