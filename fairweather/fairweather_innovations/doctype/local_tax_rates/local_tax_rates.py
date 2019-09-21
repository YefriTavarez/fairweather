# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LocalTaxRates(Document):
	def onload(self):
		pass

	def autoname(self):
		self.name = "{code} - {location}".format(**self.as_dict())
