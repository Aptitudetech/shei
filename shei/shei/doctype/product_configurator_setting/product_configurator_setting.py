# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe.model.document import Document

class ProductConfiguratorSetting(Document):

	#def before_save(self):
		# Get Child Table from Single Doctype:
	#	deposit = frappe.get_all('Deposit Setting', fields=['*'], filters={'parenttype': 'Customer Deposit Setup', 'parent': 'Customer Deposit Setup'})
     #       * Deposit Setting = Name of the Child Doctype
      #      * Customer Deposit Setup = Name of Main Doctype

# 'Play' with child table
    #if you want to update some values inside a child table when you save a doc:

    def validate(self):
		for child in self.get('list_thickness'):
			child.name = child.tickness + " - " + child.product
			pattern = "^[0-9./]*$"
			sequence = child.tickness
			if not re.match(pattern, sequence):
				frappe.throw(_("The Thickness is invalid: ").format(child.thickness))

		for child in self.get('list_environment'):
#			if "-" in child.environment:
#				frappe.throw("Sorry, the environment name can't contains '-' caractere")
			child.name = child.environment + " - " + child.product

		for child in self.get('list_finish'):
#			if "-" in child.environment:
#				frappe.throw("Sorry, the environment name can't contains '-' caractere")
			child.name = child.finish_name + " - " + child.product
			
		for child in self.get('list_cut'):
			#			if "-" in child.environment:
#				frappe.throw("Sorry, the environment name can't contains '-' caractere")
			child.name = child.panel_cut_name + " - " + child.product

		for child in self.get('list_back'):
			#			if "-" in child.environment:
#				frappe.throw("Sorry, the environment name can't contains '-' caractere")
			child.name = child.back_finish + " - " + child.product
