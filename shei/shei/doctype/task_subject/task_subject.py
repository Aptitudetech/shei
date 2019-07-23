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

	def check_mandatory_value(self):
		if not self.task_order or not self.task_desc or not self.sub_type:
			frappe.throw(_("Please write all mandatory information"))

	def get_old_data(self, name):
		old_value = dict()
		old_value['exist'] = False
		if frappe.db.exists('Task Subject', name):
			old_value['exist'] = True
		old_value['old_task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc') or ''
                old_value['old_task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type') or ''
       	        old_value['old_task_order'] = frappe.db.get_value('Task Subject', name, 'task_order') or ''
               	old_value['old_name'] = frappe.db.get_value('Task Subject', name, 'name') or ''
		return old_value
#		return old_task_desc, old_task_subtype, old_task_order, old_name


	def update_data(self, name, disabled, task_desc, sub_type, task_order):
		if not frappe.db.exists('Task Subject', name):
			task = frappe.new_doc('Task Subject')
		else:
			task = frappe.get_doc('Task Subject', name)
		task.flags.ignore_permissions = True
		task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type, 'task_order': task_order}).save()

	def update_task_information(self):
		from frappe.model.rename_doc import rename_doc
		self.check_mandatory_value()


		old_value = self.get_old_data(self.name)
#		old_task_desc, old_task_subtype, old_task_order, old_name = self.get_old_data(self.name)
		self.update_data(self.name, self.disabled, self.task_desc, self.sub_type, self.task_order)


		new_name = self.generate_doc_name(self.sub_type, self.task_desc)
		if old_value['exist']:
			if old_value['task_desc'].upper() != self.task_desc.upper() or old_value['task_subtype'] != self.sub_type: #need to rename doc
				new_name = self.generate_doc_name(self.sub_type, self.task_desc)
				frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
				self.update_projects_tasks(old_name, new_name)
				self.update_tasks(old_name, new_name)
			if old_task_order != self.task_order:
				self.update_other_tasks(self.sub_type, self.task_order, self.name)
		frappe.msgprint(_("All tasks have been updated"))

	def update_other_tasks(self, sub_type, task_order, task_name):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order), 'disabled':False}, ['*'], order_by="task_order asc")
		if task_subjects and task_subjects[0].task_order == self.task_order: #if there two task with same order, we want to increment the rest. Otherwhise do nothing
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

