# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.model.rename_doc import rename_doc
from shei.shei.doctype.task_template.task_template import reorder_tasks_after_update
from shei.shei.doctype.task_template.task_template import get_all_task_template_from_sub_type

class TaskSubject(Document):

	def autoname(self):
		self.name = self.generate_doc_name(self.sub_type, self.task_desc)

	def generate_doc_name(self, sub_type, task_desc):
		return ("{0}-{1}".format(self.sub_type, self.task_desc)).upper()

	def get_old_data(self, name):
		'''Fetch the data from database for the given Task Subject name'''
		old_values = dict()
		old_values['task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc')
                old_values['task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type')
               	old_values['name'] = frappe.db.get_value('Task Subject', name, 'name')
               	old_values['disabled'] = frappe.db.get_value('Task Subject', name, 'disabled')
		return old_values

	def create_new_task_subject(self, name, disabled, task_desc, sub_type):
		task = frappe.new_doc('Task Subject')
                task.flags.ignore_permissions = True
                task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type}).save()

	def create_tast_template(self, sub_type, task_desc):
		task_template = frappe.new_doc('Task Template')
                task_template.flags.ignore_permissions = True
                last_task_order_template = get_all_task_template_from_sub_type(sub_type)
                if not last_task_order_template:
                	last_task_order = 0
                else:
                	last_task_order = last_task_order_template[-1].task_order
                task_template.update({'task_subject': self.generate_doc_name(sub_type, task_desc), 'task_order': last_task_order + 1}).save()

	def update_data(self, name, disabled, task_desc, sub_type):
		new_name = self.name
		if not frappe.db.exists('Task Subject', name):
			self.create_new_task_subject(name, disabled, task_desc, sub_type)
			self.create_tast_template(sub_type, task_desc)
		else:
			new_name = self.renamed_all_tasks(task_desc, name, disabled)
		return new_name

	def renamed_all_tasks(self, task_desc, name, disabled):
		'''Verify, create and/or rename everything related to task subject'''
		new_name = self.name
		old_values = self.get_old_data(self.name)
		need_renaming = False
                if old_values['task_desc'].upper() != self.task_desc.upper(): #if the descrption have changed, we need to rename the doc
                	new_name = self.generate_doc_name(self.sub_type, self.task_desc)
                        frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
                        need_renaming = True
                doc = frappe.get_doc('Task Subject', new_name)
                doc.flags.ignore_permissions = True
                doc.update({'disabled': disabled, 'task_desc': task_desc}).save()
                self.update_task_template(old_values['name'], new_name, need_renaming)
                if need_renaming:
                	self.update_projects_tasks(old_values['name'], new_name)
                        self.update_tasks(old_values['name'], new_name)
		return new_name

	def update_task_template(self, old_name, new_name, need_renaming):
		'''In case a task was disabled or renamed, update the task template accordingly'''
		reorder_tasks_after_update(self.sub_type)
		if need_renaming:
			frappe.rename_doc(doctype='Task Template', old=old_name, new=new_name, ignore_permissions=True)

	#Entry Point : Update Task button
	def update_task_info(self):
		new_doc_name = self.update_data(self.name, self.disabled, self.task_desc, self.sub_type)
		self.update_task_progression_range_order(new_doc_name, self.sub_type, self.disabled)
		self.validate_task_progression_range(self.sub_type)
		frappe.msgprint(_("Tasks have been updated"))

	def validate_task_progression_range(self, sub_type):
		# since we have 5 dots on the customer portal, the limit is set to 5.
		# The current code doesn't allow to have more or less task progression range: shei.template.pages.project.html
		nb_tpr = len(frappe.db.get_all('Task Progression Range', {'sub_type':sub_type}, 'name'))
		if nb_tpr < 5:
			frappe.msgprint(_("You need to create {0} Task Progression Range for this subtype. All the clients with a project associate with this subtype will have an error when consulting the Customer Portal").format(5 - nb_tpr))

	def update_projects_tasks(self, old_name, new_name):
		'''Update all tasks where title = old_name'''
		project_tasks = frappe.db.get_all('Project Task', { 'parenttype': 'Project', 'title':old_name }, ['title', 'name'])
                for task in project_tasks:
                        t = frappe.get_doc('Project Task', task['name'])
                        t.flags.ignore_permissions = True
                        t.update({'title': new_name}).save()

	def update_tasks(self, old_name, new_name):
		'''Update all task where task_subject = old_name'''
		tasks = frappe.db.get_all('Task', {'subject': old_name}, ['subject', 'name'])
                for task in tasks:
                        t = frappe.get_doc('Task', task['name'])
                        t.flags.ignore_permissions = True
                        t.update({'subject': new_name}).save()


	def update_task_progression_range_order(self, new_name, sub_type, disabled):
		'''Update the task subject name or task order if Task Subject have been disabled'''
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name}):
			tpr = frappe.get_doc('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name})
			tpr.flags.ignore_permissions = True
			have_replacement = self.task_have_replacement(sub_type, tpr.task_order)

			if disabled and not have_replacement: #ie the task is the last one or the last in the list. We want to have the previous or next one
				previous_task = self.get_previous_task_template(tpr.task_order, sub_type)
				tpr.update({'task_subject': previous_task['name'], 'task_order': previous_task['task_order']}).save()
			elif disabled and have_replacement: #The task order will remainns the same, but need to update the task subject
				task_names = frappe.db.get_all('Task Template', {'task_order': tpr.task_order}, 'task_subject')
				for task in task_names:
					#we have a lit of task template with the right task order. 
					#Now we need to find the Task Subject with the right subtype
					replacement_task_name = frappe.db.get_value('Task Subject', {'name':task.name, 'sub_type':sub_type}, 'name')
					if replacement_task_name:
						tpr.update({'task_subject': replacement_task_name}).save()

	def task_have_replacement(self, sub_type, tpr_task_order):
		'''Check if the current task have another task to replace it'''
                tasks_template = get_all_task_template_from_sub_type(sub_type)
                if tasks_template and tasks_template[-1].task_order == tpr_task_order: #Need to know if there's a task to replace the current one
  	        	return True
		else:
			return False

	def get_previous_task_template(self, task_order, sub_type):
		'''Return the previous Task Template based on the Task Order and subtype'''
		if task_order == 1:
			replacement_tasks = frappe.db.get_all('Task Template', {'task_order': task_order + 1}, ['name', 'task_order'])
		else:
	                replacement_tasks = frappe.db.get_all('Task Template', {'task_order': task_order - 1}, ['name', 'task_order'])
                if not replacement_tasks: #ie it was the last task
                        return
                for task in replacement_tasks:
			#since the task template don't have the subtype, we need to go throught all the task subject
			#and find the one with the same task subject with the right sub_type
                        if frappe.db.exists('Task Subject', {'name':task.name, 'sub_type':sub_type}): 
                                return frappe.db.get_value('Task Template', {'task_subject':task.name}, '*', as_dict=True)


















