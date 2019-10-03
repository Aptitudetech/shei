# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe import scrub
from frappe.utils import getdate, nowdate, flt, cint
from shei.quotation_price_configurator import get_lbracket_qty, get_zclip_qty

class ScheduleAid(object):
		def __init__(self, filters=None):
			self.filters = frappe._dict(filters or {})

		def run(self, filters):
			columns = self.get_columns(filters)
			data = self.get_data(filters)
			chart = self.get_chart_data(columns, data)
			return columns, data, None, chart

		def get_columns(self, filters):
			if self.filters['prj_type'] == 'Graphic':
				columns = [_("Project") + ":Link/Project:250"]
				columns += [_("Status") + ":text:200"]
				columns += [_("Qty Panel") + ":Link/User:150"]
				columns += [_("Total Width") + ":text:105"]
				columns += [_("Qty LBracket") + ":text:105"]
				columns += [_("Qty ZClip") + ":text:90"]
				columns += [_("Qty Wallmount Kit") + ":text:90"]
				columns += [_("Ready for production") + ":text:225"]
				columns += [_("CNC") + ":text:90"]
				columns += [_("Paint") + ":text:90"]
				columns += [_("Sublimation") + ":text:90"]
				columns += [_("Installation Hardware") + ":text:90"]
				columns += [_("Inspection") + ":text:90"]
			else:
				columns = [_("Project") + ":Link/Project:250"]
				columns += [_("Status") + ":text:200"]
			return columns

		def get_data(self, filters):
			tuple_list = []
			projects = frappe.db.get_all('Project', {'status': 'Open', 'type': self.filters['prj_type']},
										 ['name', 'ready_for_production_date'])
			for project in projects:
				quote_panel_list = []
				# Quotation
				sales_order_list = frappe.db.get_all('Sales Order', {'project': project.name}, 'name')
				for so in sales_order_list:
					sales_order_items = frappe.db.get_all('Sales Order Item', {'parenttype': 'Sales Order',
																			   'parent':so.name}, 'prevdoc_docname')
					sales_order_items = {soi['prevdoc_docname']: soi for soi in sales_order_items}.values()
					for soi in sales_order_items: # we might have 1 or 2 sales order, but the second one will only have sample, no panel
						panels = frappe.db.get_all('Price Configurator Item', {'parenttype':'Quotation',
																			   'parent': soi.prevdoc_docname},
												   ['height', 'width', 'qty', 'welding_qty', 'nb_panel_with_zclip',
													'wallmount_kit_qty', 'panel_with_wallmount_lbracket'])
						measurement = frappe.db.get_value('Quotation', {'name': soi.prevdoc_docname}, 'measurement')
						quote_panel_list.extend(panels)
				if quote_panel_list:
					frappe.msgprint(_("measurement {0}").format(measurement ))

					# calculated fields
					task_name = frappe.db.get_all('Task', {'project':project.name, 'status': ('IN', 'Open, Working')},
												  'subject', order_by='task_order asc')[0]['subject']
					panel_qty = sum([int(row['qty']) for row in quote_panel_list])
					total_width = sum([float(row['width']) for row in quote_panel_list])
					frappe.msgprint(_("eqwe"))

					lbracket_qty = sum([int(get_lbracket_qty(row, measurement)) for row in quote_panel_list])
					zclip_qty = sum([int(get_zclip_qty(row, measurement)) for row in quote_panel_list])
					wallmount_kit_qty = sum([int(row['wallmount_kit_qty']) for row in quote_panel_list])
					frappe.msgprint(_("q{0}").format(task_name ))
					frappe.msgprint(_("w{0}").format(   panel_qty ))
					frappe.msgprint(_("e{0}").format( total_width ))
					frappe.msgprint(_("r{0}").format( lbracket_qty ))
					frappe.msgprint(_("t{0}").format( zclip_qty ))
					frappe.msgprint(_("y{0}").format( wallmount_kit_qty ))
					frappe.throw("{0} ".format(wallmount_kit_qty))
					cnc_time = self.get_cnc_required_time()
					paint_time = self.get_paint_required_time()
					sublimation_time = self.get_sublimation_required_time()
					installation_hardware_time = self.get_installation_required_time()
					inspection_time = self.get_inspection_required_time()
					tuple_obj = self.convert_to_tuple_obj(project.name, task_name, panel_qty, total_width, lbracket_qty,
														  zclip_qty, wallmount_kit_qty, cnc_time, paint_time,
														  sublimation_time, installation_hardware_time, inspection_time)
					tuple_list.append(tuple_obj)
			return tuple(tuple_list)  # data needs to be in Json

		def convert_to_tuple_obj(self, project, cnc_time, paint_time, pdf_end_date, installation_hardware_time,
								 inspection_time):
			obj = (project.name, project.shei_project_name, project.project_manager, project.status, project.sub_type,
				   project.expected_start_date, cnc_time, paint_time, pdf_end_date, installation_hardware_time,
				   inspection_time, self.get_preflight_time(paint_time, cnc_time),
				   self.get_printing_time(installation_hardware_time, pdf_end_date),
				   self.get_fabrication_time(inspection_time, installation_hardware_time),
				   self.get_total_time(inspection_time, project.expected_start_date),
				   )
			return obj

		def get_preflight_time(self, paint_time, cnc_time):
			if not paint_time or not cnc_time:
				return ""
			return (paint_time - cnc_time).days

		def get_printing_time(self, installation_hardware_time, sublimation_time):
			if not installation_hardware_time or not sublimation_time:
				return ""
			return (installation_hardware_time - sublimation_time).days

		def get_fabrication_time(self, inspection_time, installation_hardware_time):
			if not inspection_time or not installation_hardware_time:
				return ""
			return (inspection_time - installation_hardware_time).days

		def get_total_time(self, inspection_time, project_expected_start_date):
			if not inspection_time or not project_expected_start_date:
				return ""
			return (inspection_time - project_expected_start_date).days

		def get_cnc_required_time(self, tasks=[]):
			for task in tasks:
				if task.title.split('-')[1] == '00':
					return task.end_date

		def get_paint_required_time(self, tasks=[]):
			for task in tasks:
				if task.title.split('-')[1] == '02' and task.title.split('-')[2][0] == 'B':
					return task.end_date

		def get_sublimation_required_time(self, tasks=[]):
			for task in tasks:
				if task.title.split('-')[1] == '07':
					return task.end_date

		#			product_name = task.title.split('-')[0] #the pdf approval is different for the products Alto and Folia
		#			if product_name == 'FOLIA' and task.title.split('-')[1] == '07':
		#				return task.end_date
		#                       if product_name == 'ALTO' and task.title.split('-')[1] == '09':
		#                              return task.end_date

		def get_installation_required_time(self, tasks=[]):
			for task in tasks:
				if task.title.split('-')[1] == '06':
					return task.end_date

		def get_inspection_required_time(self, tasks=[]):
			for task in tasks:
				if task.title.split('-')[1] == '12':
					return task.end_date

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
	return ScheduleAid(filters).run(args)
