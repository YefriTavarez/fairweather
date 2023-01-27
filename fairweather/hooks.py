# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "fairweather"
app_title = "Fairweather Innovations"
app_publisher = "Yefri Tavarez"
app_description = "Fairweather Innovations custom app and ERPNext customizations"
app_icon = "octicon octicon-flame"
app_color = "#146"
app_email = "yefritavarez@gmail.com"
app_license = "General Public License, v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/fairweather/css/fairweather.css"
app_include_js = "/assets/js/fairweather.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/fairweather/css/fairweather.css"
# web_include_js = "/assets/fairweather/js/fairweather.js"

# include js in page
page_js = {
    "print": [
        "public/js/pages/print.js",
    ],
}

# include js in doctype views
doctype_js = {
    "Item": [
        "public/js/doctype/item.js",
    ],
    "Customer": [
        "public/js/doctype/customer.js",
        "fairweather/fairweather_innovations/report/statement_of_accounts/statement_of_accounts.html",
    ],
    "Sales Order": [
        "public/js/doctype/sales_order.js",
    ],
    "Sales Invoice": [
        "public/js/doctype/sales_invoice.js",
    ],
    "Delivery Note": [
        "public/js/doctype/delivery_note.js",
    ],
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# "Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "fairweather.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "fairweather.install.before_install"
# after_install = "fairweather.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fairweather.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item": {
        "after_insert": "fairweather.events.item.after_insert",
    },
    "Contact": {
        "validate": "fairweather.events.contact.validate",
    },
    "Customer": {
        "onload": "fairweather.controllers.customer.onload",
    },
    "Sales Invoice": {
        "validate": "fairweather.controllers.sales_invoice.validate",
    },
    "Sales Order": {
        "validate": "fairweather.controllers.sales_order.validate",
    },
    "Delivery Note": {
        "validate": "fairweather.controllers.delivery_note.validate",
    },
}


default_mail_footer = """
    <div style="text-align: left; font-size: 10px; color: #999;">
        <p>
            <a href="https://www.seaviewglobal.com/" target="_blank">
                SEAVIEW GLOBAL
            </a>
        </p>
        <p>
            <a href="https://www.seaviewglobal.com/pages/privacy-policy" target="_blank">
                Privacy Policy
            </a>
        </p>
    </div>
"""

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"fairweather.tasks.all"
# 	],
# 	"daily": [
# 		"fairweather.tasks.daily"
# 	],
# 	"hourly": [
# 		"fairweather.tasks.hourly"
# 	],
# 	"weekly": [
# 		"fairweather.tasks.weekly"
# 	]
# 	"monthly": [
# 		"fairweather.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "fairweather.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "fairweather.event.get_events"
# }

on_session_creation = "fairweather.sessions.before_login"
