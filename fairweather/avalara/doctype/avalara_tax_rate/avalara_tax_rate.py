# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class AvalaraTaxRate(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		self.title = f"{self.zip_code} {self.tax_region_name}"