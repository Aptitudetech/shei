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
		if frappe.db.exists('Dropdown Options', {'doctype_type': self.doctype_type, 'variable_name': self.variable_name, 'option_label': self.option_label}, 'name'):
			frappe.throw(_("Sorry, this option already exist for that document"))
		if self.value_is_a_price:
			try:
				price = round(float(self.option_value), 2)
			except ValueError:
				frappe.throw(_("The 'Option Value' couldn't be converted into a price. Please make sure the format is: 999 or 999.00"))