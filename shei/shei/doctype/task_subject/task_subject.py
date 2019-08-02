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

	def update_data(self, name, disabled, task_desc, sub_type, task_order, assigned_to):
		new_name = self.name
		if not frappe.db.exists('Task Subject', name):
			task = frappe.new_doc('Task Subject')
			task.flags.ignore_permissions = True
			task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type, 'task_order': task_order, 'assigned_to': assigned_to}).save()
		else:
			need_renaming = False
			old_values = self.get_old_data(self.name)
                        if old_values['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
                                new_name = self.generate_doc_name(self.sub_type, self.task_desc)
                                frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
				need_renaming = True
                        doc = frappe.get_doc('Task Subject', new_name)
                        doc.flags.ignore_permissions = True
			doc.update({'disabled': disabled, 'task_desc': task_desc, 'task_order': task_order, 'assigned_to': assigned_to}).save()
			if need_renaming:
                                self.update_projects_tasks(old_values['name'], new_name)
                                self.update_tasks(old_values['name'], new_name)
		return new_name

	def update_task_info(self):
		old_values = []
		if not self.is_new():
                        old_values = self.get_old_data(self.name)
		new_doc_name = self.update_data(self.name, self.disabled, self.task_desc, self.sub_type, self.task_order, self.assigned_to)
		self.update_other_tasks(self.sub_type, self.task_order, new_doc_name)
		self.reorder_tasks_after_update()
		self.update_task_progression_range_order(self.task_order, new_doc_name, self.sub_type)
		self.validate_task_progression_range(self.sub_type)
		frappe.msgprint(_("Tasks have been updated"))

	def validate_task_progression_range(self, sub_type):
		nb_tpr = len(frappe.db.get_all('Task Progression Range', {'sub_type':sub_type}, 'name'))
		if nb_tpr < 5:
			frappe.msgprint(_("You need to create {0} Task Progression Range for this subtype. All the clients with a project associate with this subtype will have an error when consulting the Customer Portal").format(5 - nb_tpr))

	def reorder_tasks_after_update(self):
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
                        t.update({'subject': new_name}).save()

	def update_task_progression_range_order(self, task_order, new_name, sub_type):
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name}):
			tpr = frappe.get_doc('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name})
			tpr.flags.ignore_permissions = True
			have_replacement = frappe.db.exists('Task Subject', {'task_order': task_order, 'sub_type':sub_type})
			if self.disabled and not have_replacement: #ie the task is the last one in the list. We want to have the previous one
				next_task = frappe.db.get_values('Task Subject', {'task_order': task_order - 1, 'sub_type':sub_type}, ['name', 'task_order'], as_dict=True)
				tpr.update({'task_oder': next_task['task_order'], 'task_subject': new_task['name']})
			elif self.disabled and have_replacement: #The task order will remainns the same, but need to update the task subject
				replacement_task_name = frappe.db.get_value('Task Subject', {'task_order': task_order, 'sub_type':sub_type}, 'task_order')
				tpr.update({'task_subject': replacement_task_name})
			else:
				tpr.update({'task_oder': task_order})
			tpr.save()
