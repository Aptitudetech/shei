# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from __future__ import division
import frappe
from frappe import _
from frappe.model.document import Document

class SOWorkOrder(Document):
	def before_save(self):
		for item in self.work_order_items:
			product = item.item_code.split('-')[0]
			if product in ['ALTO', 'FOLIA']:
				#thickness = item.item_code.split('-')[2]
				#if len(thickness.split('/')) == 2:
				#	thickness = int(thickness.split('/')[0]) / int(thickness.split('/')[1])
				#weight_per_sqft = frappe.db.get_value('Panel Thickness', {'parenttype': 'Price Configurator Setting', 'parent': 'Price Configurator Setting', 'thickness': thickness, 'product':product}, 'panel_weight')
				try:
					if item.measurement == 'MM':
						sqft = (int(item.width) / 304.8) * (int(item.height) / 304.8)
					elif item.measurement == 'Inches':
						sqft = (int(item.width) / 12) * (int(item.height) / 12)
				except ValueError, UnboundLocalError:
					frappe.msgprint(_("Sorry, some height/width are empty or have been change since last time. The value of sqft have been set to 0. <br> To change the value, you need to set a height and width manually in <strong>SO Work Order/{0}</strong> for the following item: {1}").format(self.name, item.item_code))
					sqft = 0
					
				#frappe.msgprint(_("sqft: {0} * weight_per_sqft: {1} * item.quantity: {2}").format(sqft, weight_per_sqft, item.quantity))
				#item.net_weight = sqft * weight_per_sqft * item.quantity

