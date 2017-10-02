#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe

def execute():
	if not frappe.db.exists('Custom Field', 'Contact-title'):
		return

	frappe.db.sql('''
		UPDATE `tabContact` SET designation = title 
		WHERE ifnull(designation, "")= ""
			AND ifnull(title, "") != "";
	''')

	frappe.new_doc('Property Setter').update({
		"doctype_of_field": "DocField",
		"doc_type": "Contact",
		"field_name": "designation",
		"property": "label",
		"property_type": "Data",
		"default_value": "Designation",
		"value": "Title"
	}).insert()

	frappe.delete_doc('Custom Field', 'Contact-title');