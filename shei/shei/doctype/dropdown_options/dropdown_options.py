# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _


class DropdownOptions(Document):

	def get_valid_variable_name(self):
		variables = frappe.db.get_all('DocField', {'parenttype': 'Doctype', 'parent': self.doctype_type, 'fieldtype': 'Select'}, ['fieldname'])
		return [v['fieldname'] for v in variables]


	def validate(self):
		if self.value_is_a_price and self.option_value:
			try:
				price = round(float(self.option_value), 2)
			except ValueError:
				frappe.throw(_("The 'Option Value' couldn't be converted into a price. Please make sure the format is: 999 or 999.00"))