# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class TaskSubject(Document):

	def autoname(self):
		self.name = self.generate_doc_name(self.sub_type, self.task_desc)

	def generate_doc_name(self, sub_type, task_desc):
		return ("{0}-{1}".format(self.sub_type, self.task_desc)).upper()

	def validate(self):
		conflict_sub_type = frappe.db.get_value("Task Subject", {'task_order': self.task_order, 'sub_type': self.sub_type}, 'sub_type')
		if conflict_sub_type:
			self.update_other_tasks(self.sub_type, self.task_order, self.name)
			frappe.msgprint(_("All tasks have been updated"))

#	def after_rename(self, old, new, merge=False):
#		frappe.msgprint(_("{0} - {1} <br>  {2} - {3}").format(new.split('-')[1], self.task_desc,  new.split('-')[0], self.sub_type))
#
#		if self.sub_type.upper() != new.split('-')[0] or self.task_desc.upper() != new.split('-')[1]:
#			frappe.throw(_("Please use the 'Update Task Information' button to rename the task"))
	def check_mandatory_value(self):
		if not self.task_order or not self.task_desc or not self.sub_type:
			frappe.throw(_("Please write all mandatory information"))

	def update_task_information(self):
		from frappe.model.rename_doc import rename_doc
		self.check_mandatory_value()
		old_task_desc = frappe.db.get_value('Task Subject', self.name, 'task_desc')
		old_task_subtype = frappe.db.get_value('Task Subject', self.name, 'sub_type')
		old_task_order = frappe.db.get_value('Task Subject', self.name, 'task_order')
		old_name = frappe.db.get_value('Task Subject', self.name, 'name')
		new_name = self.generate_doc_name(self.sub_type, self.task_desc)
		frappe.db.set_value('Task Subject', self.name, 'task_desc', self.task_desc)
		frappe.db.set_value('Task Subject', self.name, 'sub_type', self.sub_type)
		frappe.db.set_value('Task Subject', self.name, 'task_order', self.task_order)
		if old_task_desc.upper() != self.task_desc.upper() or old_task_subtype != self.sub_type:
			new_name = self.generate_doc_name(self.sub_type, self.task_desc)
			frappe.rename_doc(self.doctype, self.name, new_name)
			self.update_projects_tasks(old_name, new_name)
			self.update_tasks(old_name, new_name)
		if old_task_order != self.task_order:
			self.update_other_tasks(self.sub_type, self.task_order, self.name)
		frappe.msgprint(_("All tasks have been updated"))

	def update_other_tasks(self, sub_type, task_order, task_name):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order)}, ['*'])
		for subject in task_subjects:
			doc = frappe.get_doc('Task Subject', subject['name'])
			new_order = int(doc.task_order) + 1
			doc.flags.ignore_permissions = True
			doc.update({'task_order': new_order}).save()

	def update_projects_tasks(self, old_name, new_name):
		project_tasks = frappe.db.get_all('Project Task', { 'parenttype': 'Project', 'title':old_name }, ['title', 'name'])
                for task in project_tasks:
                        t = frappe.get_doc('Project Task', task['name'])
                        t.flags.ignore_permissions = True
                        t.update({'title': new_name}).save()

	def update_tasks(self, old_name, new_name):
		tasks = frappe.db.get_all('Task', {'subject': old_name}, ['subject', 'name'])
                for task in tasks:
                        t = frappe.get_doc('Task', task['name'])
                        t.flags.ignore_permissions = True
                        t.update({'subject': new_name}).save()

