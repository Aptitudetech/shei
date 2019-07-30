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

	def get_old_data(self, name):
		old_values = dict()
		old_values['task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc')
                old_values['task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type')
       	        old_values['task_order'] = frappe.db.get_value('Task Subject', name, 'task_order')
               	old_values['name'] = frappe.db.get_value('Task Subject', name, 'name')
               	old_values['disabled'] = frappe.db.get_value('Task Subject', name, 'disabled')
               	old_values['is_being_updated'] = frappe.db.get_value('Task Subject', name, 'is_being_updated')
		return old_values

	def update_data(self, name, disabled, task_desc, sub_type, task_order):
		if not frappe.db.exists('Task Subject', name):
			task = frappe.new_doc('Task Subject')
		else:
			task = frappe.get_doc('Task Subject', name)
		task.flags.ignore_permissions = True
		task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type, 'task_order': task_order}).save()
		redirect = self.update_task_name(name, task_desc, sub_type)
		return redirect

	def update_task_name(self, name, task_desc, sub_type):
		old_values = self.get_old_data(name)
		redirect = False
		if not self.is_new():
			if old_values['task_desc'].upper() != task_desc.upper(): #need to rename doc
		                new_name = self.generate_doc_name(sub_type, task_desc)
                	        frappe.rename_doc(doctype="Task Subject", old=name, new=new_name, ignore_permissions=True)
				redirect = True
		return redirect

	def validate_task_order(self, task_order, is_being_updated, sub_type):
		if task_order == 0: #the 0 might break something in the Project Task table (2 idx will be = 1)
                        self.task_order = 1

	def update_task_info(self):
		from frappe.model.rename_doc import rename_doc
		old_values = []
		if not self.is_new():
                        old_values = self.get_old_data(self.name)
		self.validate_task_order(self.task_order, self.is_being_updated, self.sub_type)
		redirect = self.update_data(self.name, self.disabled, self.task_desc, self.sub_type, self.task_order)

		if old_values:
			self.update_other_tasks(self.sub_type, self.task_order, self.name)
			self.reorder_tasks_after_update(old_values)
		if self.is_new():
			self.update_other_tasks(self.sub_type, self.task_order, self.name)
			self.reorder_tasks_after_update(old_values)
		return redirect

	def reorder_tasks_after_update(self, old_values=[]):
		tasks = frappe.db.get_all('Task Subject', {'sub_type': self.sub_type, 'disabled':False}, ['task_order', 'name'], order_by='task_order asc')
		task_order = 1
		for task in tasks:
			if task.task_order != task_order: #we don't want to update it if already alright
				doc = frappe.get_doc('Task Subject', task['name'])
	                        doc.flags.ignore_permissions = True
	       	                doc.update({'task_order':task_order}).save()
			task_order = task_order + 1

	def update_other_tasks(self, sub_type, task_order, task_name):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order), 'disabled':False}, ['name'], order_by="task_order asc")
		#if there two task with same order, we want to increment the rest. Otherwhise do nothing
		if task_subjects and task_subjects[0].task_order == self.task_order:
			new_task_order = self.task_order
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
                        t.update({'subject': new_name}).save()

