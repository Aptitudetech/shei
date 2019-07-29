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

	def update_task_name(self):
		old_values = self.get_old_data(self.name)
		if old_values['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
	                new_name = self.generate_doc_name(self.sub_type, self.task_desc)
                        frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
			doc = frappe.get_doc('Task Subject', new_name)
			doc.flags.ignore_permissions = True
                        doc.update({'task_desc':self.task_desc, 'is_being_updated':True}).save()
                        self.update_projects_tasks(old_values['name'], new_name)
                        self.update_tasks(old_values['name'], new_name)
			self.reset_is_being_updated_field()

	def validate_task_order(self, task_order, is_being_updated, sub_type, old_values=[]):
		if task_order == 0: #the 0 might break something in the Project Task table (2 idx will be = 1)
                        self.task_order = 1
		if old_values:
			first_task = frappe.db.get_value('Task Subject', {'sub_type':sub_type, 'disabled':False, 'task_order':1}, 'name')
                        if old_values['task_order'] == 1 and task_order == 2 and not first_task: 
				#means the first task have changed, but nothing have been created to replace it. ie: first_task task_order will be 2
                                frappe.throw(_("Invalid Task Order. Please create/update a task order to 1 to update this one"))

	def validate_task_desc(self, is_new, is_being_updated, task_name, task_desc, old_values=[]):
		if old_values:
                        if old_values['task_desc'].upper() != task_desc.upper(): #need to rename doc
                                frappe.throw(_("To update the task description, please use the button 'Update Task Description'"))

	def validate(self):
		from frappe.model.rename_doc import rename_doc
		old_values = []
		if not self.is_new() and self.is_being_updated == False:
                        old_values = self.get_old_data(self.name)
		self.validate_task_order(self.task_order, self.is_being_updated, self.sub_type, old_values)
		self.validate_task_desc(self.is_new(), self.is_being_updated, self.name, self.task_desc, old_values)
		if old_values:
			if old_values['is_being_updated'] == self.is_being_updated: #we want to execute this code once. Recursion forces us to add this condition
				self.update_other_tasks(self.sub_type, self.task_order, self.name)
				self.reorder_tasks_after_update(old_values)
        	                self.reset_is_being_updated_field()
		if self.is_new() and self.is_being_updated == False: #new doc
			self.update_other_tasks(self.sub_type, self.task_order, self.name)

	def reorder_tasks_after_update(self, old_values=[]):
		tasks = frappe.db.get_all('Task Subject', {'sub_type': self.sub_type, 'disabled':False, 'name': ('!=', self.name)}, ['task_order', 'name'], order_by='task_order asc')
		task_order = 1
		if (old_values['disabled'] == True and self.disabled == False) or (int(tasks[-1]['task_order']) < self.task_order):
			#newly enabled, the update_other_tasks() have ordered the task, except if it's the last one in the list (ie biggest task_order)
			#last_task = frappe.db.get_list('Task Subject', {'sub_type': self.sub_type, 'disabled':False}, ['task_order', 'name'], order_by='task_order desc', limit=1)[0]
			last_task_order = int(tasks[-1]['task_order']) + 1
			self.task_order = last_task_order
			return
		for task in tasks:
			if task_order == self.task_order:
				self.task_order = task_order
			elif task['task_order'] != task_order:
#			else:
				doc = frappe.get_doc('Task Subject', task['name'])
	                        doc.flags.ignore_permissions = True
	       	                doc.update({'task_order':task_order, 'is_being_updated':True}).save()
				continue
			task_order = task_order + 1


	def update_other_tasks(self, sub_type, task_order, task_name):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order), 'disabled':False}, ['*'], order_by="task_order asc")
		#if there two task with same order, we want to increment the rest. Otherwhise do nothing
		if task_subjects and task_subjects[0].task_order == self.task_order:
			for subject in task_subjects:
				doc = frappe.get_doc('Task Subject', subject['name'])
				doc.flags.ignore_permissions = True
				doc.update({'task_order':doc.task_order + 1, 'is_being_updated':True}).save()

	def reset_is_being_updated_field(self):
		task_subjects = frappe.db.get_all('Task Subject', {'is_being_updated': True}, 'name')
		for subject in task_subjects:
			doc = frappe.get_doc('Task Subject', subject['name'])
                        doc.flags.ignore_permissions = True
                        doc.update({'is_being_updated':False}).save()

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

