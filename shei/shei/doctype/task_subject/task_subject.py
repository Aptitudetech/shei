# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.model.rename_doc import rename_doc

class TaskSubject(Document):

	def autoname(self):
		self.name = self.generate_doc_name(self.sub_type, self.task_desc)

	def generate_doc_name(self, sub_type, task_desc):
		return ("{0}-{1}".format(self.sub_type, self.task_desc)).upper()

	def get_old_data(self, name):
		old_values = dict()
		old_values['task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc')
                old_values['task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type')
       	        old_values['task_order'] = frappe.db.get_value('Task Subject', name, 'task_order')
               	old_values['name'] = frappe.db.get_value('Task Subject', name, 'name')
               	old_values['disabled'] = frappe.db.get_value('Task Subject', name, 'disabled')
		return old_values

	def update_data(self, name, disabled, task_desc, sub_type, task_order):
		new_name = self.name
		if not frappe.db.exists('Task Subject', name):
			task = frappe.new_doc('Task Subject')
			task.flags.ignore_permissions = True
			task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type, 'task_order': task_order}).save()
		else:
			need_renaming = False
			old_values = self.get_old_data(self.name)
                        if old_values['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
                                new_name = self.generate_doc_name(self.sub_type, self.task_desc)
                                frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
				need_renaming = True
                        doc = frappe.get_doc('Task Subject', new_name)
                        doc.flags.ignore_permissions = True
			doc.update({'disabled': disabled, 'task_desc': task_desc, 'task_order': task_order}).save()
			if need_renaming:
                                self.update_projects_tasks(old_values['name'], new_name)
                                self.update_tasks(old_values['name'], new_name)
		return new_name

	def validate_task_order(self, task_order):
		if task_order == 0: #the 0 might break something in the Project Task table (2 idx will be = 1)
                        self.task_order = 1

	def update_task_info(self):
		old_values = []
		if not self.is_new():
                        old_values = self.get_old_data(self.name)
		self.validate_task_order(self.task_order)
		new_doc_name = self.update_data(self.name, self.disabled, self.task_desc, self.sub_type, self.task_order)
		self.update_other_tasks(self.sub_type, self.task_order, new_doc_name)
		self.reorder_tasks_after_update()

	def reorder_tasks_after_update(self):
		tasks = frappe.db.get_all('Task Subject', {'sub_type': self.sub_type, 'disabled':False}, ['task_order', 'name'], order_by='task_order asc')
		for t in tasks:
			frappe.msgprint(_("t: {0}  --  tn: {1}").format(t.task_order, t.name))

		task_order = 1
		for task in tasks:
			if task.task_order != task_order: #we don't want to update it if already alright
				doc = frappe.get_doc('Task Subject', task['name'])
	                        doc.flags.ignore_permissions = True
	       	                doc.update({'task_order':task_order}).save()
			task_order = task_order + 1

	def update_other_tasks(self, sub_type, task_order, task_name):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order), 'disabled':False}, ['name', 'task_order'], order_by="task_order asc")
		#if there two task with same order, we want to increment the rest. Otherwhise do nothing
		if task_subjects and task_subjects[0].task_order == task_order:
			new_task_order = task_order + 1
			for subject in task_subjects:
				doc = frappe.get_doc('Task Subject', subject['name'])
				doc.flags.ignore_permissions = True
				doc.update({'task_order':new_task_order}).save()
				new_task_order = new_task_order + 1

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
			frappe.msgprint(_("tn: {0}  --  tat: {1}  ---  tp: {2}").format(t.name, t.assigned_to, t.project))
                        t.update({'subject': new_name}).save()

