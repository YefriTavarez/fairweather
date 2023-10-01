# -*- coding: utf-8 -*-
# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

from functools import lru_cache

from jinja2 import TemplateError

import frappe

from frappe import _
from frappe.utils import add_to_date, nowdate, cast
from frappe.email.doctype.notification import notification


from frappe.modules.utils import get_doc_module
from frappe.email.doctype.notification.notification import (
    Notification as FrappeNotification,
    get_context,
)


class Notification(FrappeNotification):
    # @override
    def validate_condition(self):
        temp_doc = frappe.new_doc(self.document_type)
        if self.condition:
            try:
                frappe.safe_eval(
                    self.condition,
                    None,
                    self.get_whole_context(
                        temp_doc.as_dict()
                    )
                )
            except Exception:
                frappe.log_error()
                frappe.throw(
                    f"The Condition '{self.condition}' is invalid"
                )
    
    # @override
    def get_documents_for_today(self):
        """get list of documents that will be triggered today"""
        docs = []

        diff_days = self.days_in_advance
        if self.event == "Days After":
            diff_days = -diff_days

        reference_date = add_to_date(nowdate(), days=diff_days)
        reference_date_start = reference_date + " 00:00:00.000000"
        reference_date_end = reference_date + " 23:59:59.000000"

        doc_list = frappe.get_all(
            self.document_type,
            fields="name",
            filters=[
                {self.date_changed: (">=", reference_date_start)},
                {self.date_changed: ("<=", reference_date_end)},
            ],
        )

        for d in doc_list:
            doc = frappe.get_doc(self.document_type, d.name)

            context = self.get_whole_context(doc)

            if self.condition and not frappe.safe_eval(
                self.condition,
                None,
                context
            ):
                continue

            docs.append(doc)

        return docs

    def get_whole_context(self, doc):
        if isinstance(doc, frappe.model.document.Document):
            doc = doc.as_dict()

        base_context = get_context(doc)

        module = get_doc_module(self.module, self.doctype, self.name)
        if module:
            if hasattr(module, "get_context"):
                out = module.get_context(base_context)
                if out:
                    base_context.update(out)

        return base_context


def custom_evaluate_alert(doc, alert, event):

    try:
        if isinstance(alert, str):
            alert = frappe.get_doc("Notification", alert)

        context = alert.get_whole_context(doc)

        if alert.condition:
            if not frappe.safe_eval(alert.condition, None, context):
                return

        if event == "Value Change" and not doc.is_new():
            if not frappe.db.has_column(doc.doctype, alert.value_changed):
                alert.db_set("enabled", 0)
                alert.log_error(
                    f"Notification {alert.name} has been disabled due to missing field")
                return

            doc_before_save = doc.get_doc_before_save()
            field_value_before_save = doc_before_save.get(
                alert.value_changed) if doc_before_save else None

            fieldtype = doc.meta.get_field(alert.value_changed).fieldtype
            if cast(fieldtype, doc.get(alert.value_changed)) == cast(fieldtype, field_value_before_save):
                # value not changed
                return

        if event != "Value Change" and not doc.is_new():
            # reload the doc for the latest values & comments,
            # except for validate type event.
            doc.reload()
        alert.send(doc)
    except TemplateError:
        frappe.throw(
            _("Error while evaluating Notification {0}. Please fix your template.").format(
                alert)
        )
    except Exception as e:
        error_log = frappe.log_error(
            message=frappe.get_traceback(), title=str(e))
        frappe.throw(
            _("Error in Notification: {}").format(
                frappe.utils.get_link_to_form("Error Log", error_log.name)
            )
        )
