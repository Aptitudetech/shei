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
				thickness = item.item_code.split('-')[2]
				if len(thickness.split('/')) == 2:
					thickness = int(thickness.split('/')[0]) / int(thickness.split('/')[1])
				weight_per_sqft = frappe.db.get_value('Panel Thickness', {'parenttype': 'Price Configurator Setting', 'parent': 'Price Configurator Setting', 'thickness': thickness, 'product':product}, 'panel_weight')
				if item.measurement == 'MM':
					sqft = (item.width / 304.8) * (item.height / 304.8)
				elif item.measurement == 'Inches':
					sqft = (item.width / 12) * (item.height / 12)
				item.net_weight = sqft * weight_per_sqft * item.quantity