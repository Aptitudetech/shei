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
		old_value['task_desc'] = frappe.db.get_value('Task Subject', name, 'task_desc')
                old_value['task_subtype'] = frappe.db.get_value('Task Subject', name, 'sub_type')
       	        old_value['task_order'] = frappe.db.get_value('Task Subject', name, 'task_order')
               	old_value['name'] = frappe.db.get_value('Task Subject', name, 'name')
               	old_value['disabled'] = frappe.db.get_value('Task Subject', name, 'disabled')
		return old_value

	def update_task_name(self):
		old_value = self.get_old_data(self.name)
		if old_value['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
	                new_name = self.generate_doc_name(self.sub_type, self.task_desc)
                        frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
			doc = frappe.get_doc('Task Subject', new_name)
			doc.flags.ignore_permissions = True
                        doc.update({'task_desc': self.task_desc, 'is_being_updated':True}).save()
                        self.update_projects_tasks(old_value['name'], new_name)
                        self.update_tasks(old_value['name'], new_name)
			self.reset_is_being_updated_field()

	def validate(self):
		from frappe.model.rename_doc import rename_doc
		if self.task_order == 0: #the 0 might break something in the Project Task table (2 idx will be = 1)
                        self.task_order = 1

		if not self.is_new() and self.is_being_updated == False:
			old_value = self.get_old_data(self.name)
                        if old_value['task_desc'].upper() != self.task_desc.upper(): #need to rename doc
                                new_name = self.generate_doc_name(self.sub_type, self.task_desc)
#                                self.name = new_name
                                frappe.rename_doc(doctype=self.doctype, old=self.name, new=new_name, ignore_permissions=True)
                                self.update_projects_tasks(old_value['name'], new_name)
                                self.update_tasks(old_value['name'], new_name)
                        if old_value['task_order'] != self.task_order or (old_value['disabled'] == True and self.disabled == False): #order changed or task is no longer disabled
                                self.update_other_tasks(self.sub_type, self.task_order, self.name, True)
				if old_value['disabled'] == True and self.disabled == False and self.task_order > int(frappe.db.get_value('Task Subject', {'sub_type': self.sub_type, 'disabled':False}, 'task_order', order_by='task_order desc')):
					#if we are reenabling the last task, the task number might not match the previous task_order
					self.update_last_task_after_reenable()
					self.reset_is_being_updated_field()

                        if old_value['disabled'] == False and self.disabled == True: #task have been disabled
                                self.update_other_tasks(self.sub_type, self.task_order, self.name, False)

		if self.is_new() and self.is_being_updated == False: #new doc
			self.update_other_tasks(self.sub_type, self.task_order, self.name)

	def update_last_task_after_reenable(self):
		last_tasks = frappe.db.get_list('Task Subject', {'sub_type': self.sub_type, 'disabled':False}, ['task_order', 'name'], order_by='task_order desc', limit=1)
		last_task_order = int(last_tasks[0].task_order) + 1
		self.task_order = last_task_order

	def update_other_tasks(self, sub_type, task_order, task_name, task_order_increase):
		"""Update the order of other tasks"""
		task_subjects = frappe.db.get_all('Task Subject', {'sub_type':sub_type, 'name': ('!=', task_name), 'task_order': ('>=', task_order), 'disabled':False}, ['*'], order_by="task_order asc")
		#if there two task with same order, we want to increment the rest. Otherwhise do nothing
		if task_subjects and (task_subjects[0].task_order == self.task_order or task_order_increase == False):
			for subject in task_subjects:
				doc = frappe.get_doc('Task Subject', subject['name'])
				if task_order_increase:
					new_order = int(doc.task_order) + 1
				else:
					new_order = int(doc.task_order) - 1
				doc.flags.ignore_permissions = True
				doc.update({'task_order':new_order, 'is_being_updated':True}).save()
#			if task_order_increase == False:
#				self.update_last_task_after_reenable()
			self.reset_is_being_updated_field()

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

