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
		old_values = dict()
		old_values['task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc')
                old_values['task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type')
               	old_values['name'] = frappe.db.get_value('Task Subject', name, 'name')
               	old_values['disabled'] = frappe.db.get_value('Task Subject', name, 'disabled')
		return old_values

	def update_data(self, name, disabled, task_desc, sub_type):
		new_name = self.name
		if not frappe.db.exists('Task Subject', name):
			task = frappe.new_doc('Task Subject')
			task.flags.ignore_permissions = True
			task.update({'disabled': disabled, 'task_desc': task_desc, 'sub_type': sub_type}).save()
			task_template = frappe.new_doc('Task Template')
                        task_template.flags.ignore_permissions = True
			last_task_order_template = get_all_task_template_from_sub_type(sub_type)
			if not last_task_order_template:
				last_task_order = 0
			else:
				last_task_order = last_task_order_template[-1].task_order
                        task_template.update({'task_subject': self.generate_doc_name(sub_type, task_desc), 'task_order': last_task_order + 1}).save()
		else:
			need_renaming = False
			old_values = self.get_old_data(self.name)
                        if old_values['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
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
		reorder_tasks_after_update(self.sub_type)
		if need_renaming:
			frappe.rename_doc(doctype='Task Template', old=old_name, new=new_name, ignore_permissions=True)

	def update_task_info(self):
		old_values = []
		if not self.is_new():
                        old_values = self.get_old_data(self.name)
		new_doc_name = self.update_data(self.name, self.disabled, self.task_desc, self.sub_type)
		self.update_task_progression_range_order(new_doc_name, self.sub_type)
		self.validate_task_progression_range(self.sub_type)
		frappe.msgprint(_("Tasks have been updated"))

	def validate_task_progression_range(self, sub_type):
		nb_tpr = len(frappe.db.get_all('Task Progression Range', {'sub_type':sub_type}, 'name'))
		if nb_tpr < 5:
			frappe.msgprint(_("You need to create {0} Task Progression Range for this subtype. All the clients with a project associate with this subtype will have an error when consulting the Customer Portal").format(5 - nb_tpr))

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


	def update_task_progression_range_order(self, new_name, sub_type):
		if frappe.db.exists('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name}):
			tpr = frappe.get_doc('Task Progression Range', {'sub_type': sub_type, 'task_subject': new_name})
			tpr.flags.ignore_permissions = True
			have_replacement = False
			tasks_template = get_all_task_template_from_sub_type(sub_type)
			if tasks_template and tasks_template[-1].task_order == tpr.task_order:
				have_replacement = True

			if self.disabled and not have_replacement: #ie the task is the last one in the list. We want to have the previous one
				next_task = self.task_get_next_task_template(tpr.task_order, sub_type)
				tpr.update({'task_subject': new_task['name'], 'task_order': new_task['task_order']})
			elif self.disabled and have_replacement: #The task order will remainns the same, but need to update the task subject
				task_names = frappe.db.get_all('Task Template', {'task_order': tpr.task_order}, 'task_subject')
				for task in task_names:
					replacement_task_name = frappe.db.get_value('Task Subject', {'name':task.name, 'sub_type':sub_type}, 'name')
					if replacement_task_name:
						tpr.update({'task_subject': replacement_task_name})
			tpr.save()

	def task_get_next_task_template(self, task_order, sub_type):
                next_task = frappe.db.get_all('Task Template', {'task_order': task_order - 1}, ['name', 'task_order'])
                if not next_task:
                        return
                for task in next_task: #need to find the task Subject with sub_type
                        if frappe.exists('Task Subject', {'name':task.name, 'sub_type':sub_type}):
                                return frappe.db.get_value('Task Template', {'task_subject':task.name}, '*', as_dict=True)
