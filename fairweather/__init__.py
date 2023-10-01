# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from typing import TYPE_CHECKING

from fairweather \
    .fairweather_innovations \
    .doctype \
    .sales_by_state_item_groups \
    .sales_by_state_item_groups import get_sales_by_state_items_groups


if not TYPE_CHECKING:
    from frappe.email.doctype.notification import notification
    from fairweather.controllers.frappe.notification import custom_evaluate_alert

    # @override
    notification.evaluate_alert = custom_evaluate_alert


__version__ = '2.0.10'
