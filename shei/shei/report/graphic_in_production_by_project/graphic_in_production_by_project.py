# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

class GraphicInProductionByProject(object):
	def __init__(self, filters=None):
                self.filters = frappe._dict(filters or {})

        def run(self, filters):
                columns = self.get_columns(filters)
                data = self.get_data(filters)
                chart = self.get_chart_data(columns, data)
                return columns, data, None, chart

	def get_columns(self, filters):
		columns = [_("Sales Order") + ":Link/Sales Order:105"]
                columns += [_("Project") + ":Link/Project:250"]
                columns += [_("Exp End Date") + ":date:200"]
                columns += [_("First Open Task") + ":text:150"]
                columns += [_("Quantity") + ":text:50"]
                columns += [_("Item Code") + ":Link/Item:150"]
                return columns

        def get_data(self, filters):
                tuple_list = []
		sales_order = self.get_all_sales_order_by_graphic_sales('Graphic Sales')
		if not sales_order:
			return []
		for so in sales_order:
			sales_order_id = so.name
			project_name = so.project
			exp_end_date = frappe.db.get_value('Project', {'name': so.project}, 'expected_end_date')
			task = frappe.db.get_all('Task', {'status': ('NOT IN', 'Closed, Cancelled'), 'project':so.project}, 'subject', order_by='task_order asc', limit=1)
			if task:
				first_open_task = task[0]['subject']
			else:
				first_open_task = ""
			so_items = frappe.db.get_all('Sales Order Item', {'parenttype':'Sales Order', 'parent':so.name}, ['qty', 'item_code'])
			for item in so_items:
				quantity = item.qty
				item_code = item.item_code
				obj = (sales_order_id, project_name, exp_end_date, first_open_task, quantity, item_code)
        	                tuple_list.append(obj)
                return tuple(tuple_list) #data needs to be in Json

	def get_all_sales_order_by_graphic_sales(self, sales_person):
		sales_order = []
		all_sales_order = frappe.db.get_all('Sales Order', {'status': ('NOT IN', "Completed, Closed, Cancelled")}, '*')
		for so in all_sales_order:
                        sales_person = frappe.db.get_value('Sales Team', {'parenttype':'Sales Order', 'parent':so.name, 'sales_person':'Graphic Sales'}, 'sales_person')
			if sales_person:
				sales_order.append(so)
		return sales_order

	def get_chart_data(self, columns, data):
                return {
                        "data": {
                                'rows': data
                        },
                        "chart_type": 'pie'
                }


def execute(filters=None):
        args = {
        }
	return GraphicInProductionByProject(filters).run(args)


