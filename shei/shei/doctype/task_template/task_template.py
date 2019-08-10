# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import json

class TaskTemplate(Document):

	#Entry Point -> Update Informations button
	def update_task_template(self):
		curr_task_sub_type = frappe.db.get_value('Task Subject', self.task_subject, 'sub_type')
                self.update_other_tasks(curr_task_sub_type, self.task_order, self.task_subject)
                reorder_tasks_after_update(curr_task_sub_type)
                self.update_task_progression_range_order(self.task_order, self.task_subject)
                frappe.msgprint(_("Tasks have been updated"))

	def update_task_progression_range_order(self, task_order, task_subject):
		ts = frappe.db.get_values('Task Subject', self.name, ['sub_type', 'disabled', 'name'], as_dict=True)
                if frappe.db.exists('Task Progression Range', {'task_subject': task_subject}):
                        tpr = frappe.get_doc('Task Progression Range', {'task_subject': ts.name})
                        tpr.flags.ignore_permissions = True
                        tpr.update({'task_order': task_order})
                        tpr.save()

	def update_other_tasks(self, sub_type, task_order, task_subject):
                """Update the order of other tasks"""
		tasks_by_sub_type = get_all_task_template_from_sub_type(sub_type)
		tasks = []
		for t in tasks:
			#append all Enabled Task Subject, excluing current Task, where task_order is greater or equal current task order
			if t.task_order >= task_order and frappe.db.get_value('Task Subject', {'name':t.task_subject}, 'disabled') == False and t.task_subject != self.task_subject:
				tasks.append(t)
                #if there two task with same order, we want to increment the rest. Otherwhise do nothing
                if task_subject and task_subject != self.task_subject and tasks[0].task_order == task_order:
                        new_task_order = task_order + 1
                        for t in tasks:
                                doc = frappe.get_doc('Task Template', t['name'])
                                doc.flags.ignore_permissions = True
                                doc.update({'task_order':new_task_order}).save()
                                new_task_order = new_task_order + 1

@frappe.whitelist()
def reorder_tasks_after_update(sub_type):
	tasks = get_all_task_template_from_sub_type(sub_type)
        task_order = 1
        for task in tasks:
	        if task.task_order != task_order: #we don't want to update it if already alright
        	        doc = frappe.get_doc('Task Template', task.name)
                        doc.flags.ignore_permissions = True
                        doc.update({'task_order':task_order}).save()
                task_order = task_order + 1

@frappe.whitelist()
def get_all_task_template_from_sub_type(sub_type):
	tasks_subject = frappe.db.get_all('Task Subject', {'sub_type': sub_type, 'disabled':False}, ['name'])
	tasks = []
	for t in tasks_subject:
                task = frappe.db.get_value('Task Template', {'name':t.name}, '*')
		if task:
			tasks.append(task)
	tasks.sort(key=order_task_by_task_order, reverse=False)
	return tasks

@frappe.whitelist()
def order_task_by_task_order(json_task):
	try:
       		return int(json_task['task_order'])
    	except KeyError:
        	return 0
