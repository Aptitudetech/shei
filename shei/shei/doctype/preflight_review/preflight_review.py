# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.website.website_generator import WebsiteGenerator

class PreflightReview(WebsiteGenerator):
	def autoname(self):
		if not self.name:
			self.name = self.project
			self.pr_name = self.name

	def before_save(self):
		if self.amended_from and self.docstatus == 0:
			self.workflow_state = 'Pending'
			self.pr_name = self.name
			route = self.pr_name.replace(' ', '-').replace('(', '').replace(')', '')
			self.route = "preflight-review/{0}".format(route)

	def get_context(self, context):
		context.show_sidebar = 1

@frappe.whitelist()
def create_new_preflight_review():
	pass

@frappe.whitelist()
def amend_preflight_review(doc_name, items = []):
	doc = frappe.get_doc('Preflight Review', doc_name)
	frappe.msgprint(_("REACH {0}").format(items))
	items_json = json.loads(items)
	doc.cancel()
	new_pr = frappe.copy_doc(doc)
	new_pr.amended_from = doc.name
	new_pr.status = "Draft"
	new_pr.append('items', {})

	for i in items_json:
		frappe.msgprint(_("i: {0}").format(i))
		new_pr.append('items', i)
	new_pr.insert()