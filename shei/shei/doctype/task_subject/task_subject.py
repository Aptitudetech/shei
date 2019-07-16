# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class TaskSubject(Document):


	def after_rename(self, old, new, merge=False):
		project_tasks = frappe.db.get_all('Project Task', { 'parenttype': 'Project', 'title':old }, ['title', 'name'])
		for task in project_tasks:
			t = frappe.get_doc('Project Task', task['name'])
			t.flags.ignore_permissions = True
			t.update({'title': new}).save()
		tasks = frappe.db.get_all('Task', {'subject': old}, ['subject', 'name'])
		for task in tasks:
			t = frappe.get_doc('Task', task['name'])
			t.flags.ignore_permissions = True
			t.update({'subject': new}).save()
		self.name = new
