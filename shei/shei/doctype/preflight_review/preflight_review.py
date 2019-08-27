# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.website.website_generator import WebsiteGenerator
import re

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
def create_preflight_review(project_name):
	new_pr = frappe.new_doc('Preflight Review')
	new_pr.update({
		"project": project_name,
		"is_published": True,
	})
	new_pr.flags.ignore_permissions = True
	new_pr.save()


@frappe.whitelist()
def validate_data(items=[]):
	valid_items = []
	for i in items:
		try:
			if not i['Graphic File Name']:
				frappe.throw(_("You must write the 'Graphic File Name' for the line {}").format(i['#']))
			if not i['Measurement']:
				frappe.throw(_(
					"You must select a Measurement for the line {0}").format(i['#']))
			if i['Panel Height']:
				height = re.match('^(([0-9]*)+(([ ]?)+([0-9]+)+([/]))*(([.,]?)?([0-9]+)))$', i['Panel Height'])
				if not height:
					frappe.throw(_("You must write the 'Panel Height' for the line {0}. <br> Example of the format accepted: '1', '1 1/3', '1,33', '1.33'").format(i['#']))
			if i['Panel Width']:
				width = re.match('^(([0-9]*)+(([ ]?)+([0-9]+)+([/]))*(([.,]?)?([0-9]+)))$', i['Panel Width'])
				if not width:
					frappe.throw(_("You must write the 'Panel Width' for the line {0}. <br> Example of the format accepted: '1', '1 1/3', '1,33', '1.33'").format(i['#']))
			if not int(i['Panel Quantity']):
				frappe.throw(_("You must write a valid 'Panel Quantity' for the line {0}. Valid format(1 to 999)").format(i['#']))
		except KeyError:
			frappe.throw(_("Please fill all mandatory field: Graphic File name, Panel Height, Panel Width and Panel Quantity"))


@frappe.whitelist()
def amend_preflight_review(doc_name, items_str=[]):
	doc = frappe.get_doc('Preflight Review', doc_name)
	items_json = json.loads(items_str)
	items_json = items_json[1:]  # the first item will aways be empty, because it's the __proto__: Object from JS
	validate_data(items_json)
	doc.cancel()
	new_pr = frappe.copy_doc(doc)
	new_pr.amended_from = doc.name
	new_pr.status = "Draft"
	new_pr.set("items", [])
	items = []
	for i in items_json:
		items.append({
			'filename': i['Graphic File Name'],
			'measurement': i['Measurement'],
			'height': i['Panel Height'],
			'width': i['Panel Width'],
			'panel_qty': i['Panel Quantity'],
		})
	new_pr.set("items", items)
	new_pr.insert()
	frappe.msgprint(_("A new Document have been created with the updated information. You can access by clicking here: <a href={0}>{1}</a>").format(new_pr.route, new_pr.name))
