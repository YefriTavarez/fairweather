# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class AvalaraTaxRate(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		zip_code = f"{self.zip_code}"
		region_list = list()

		
		if self.county:
			region_list.append(self.county)

		if self.tax_region_name and self.county != self.tax_region_name:
			region_list.append(self.tax_region_name)

		regions = ", ".join(region_list)

		title = f"{zip_code} {regions}"

		self.title = title
