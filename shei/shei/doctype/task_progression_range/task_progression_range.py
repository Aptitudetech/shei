# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TaskProgressionRange(Document):

	def validate_data(self, sub_type, task_subject, color, glyphicon, progression, name):
		nb_range_sub_type = len(frappe.db.get_all('Task Progression Range', {'sub_type': sub_type, 'name': ('!=', name)}, 'name'))
		if nb_range_sub_type == 5:
			frappe.throw(_("You can only have 5 Progression Range By SubType. Please remove/update previously created progression Range"))
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'task_subject':task_subject, 'name': ('!=', name)}, 'name'):
			frappe.throw(_("The selected Task is already linked to another progress. Please choose something else"))
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'progression':progression, 'name': ('!=', name)}, 'name'):
			frappe.throw(_("A progression Range with this SubType and this Progression already exists. Please choose something else"))
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'color':color, 'name': ('!=', name)}, 'name'):
			frappe.throw(_("A progression Range with this SubType and this Color already exists. Please choose something else"))
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'glyphicon':glyphicon, 'name': ('!=', name)}, 'name'):
			frappe.throw(_("A progression Range with this SubType and this Glyphicon already exists. Please choose something else"))

	def validate(self):
		self.validate_data(self.sub_type, self.task_subject, self.color, self.glyphicon, self.progression, self.name)
