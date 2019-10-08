# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe import scrub
from frappe.utils import getdate, nowdate, flt, cint
from shei.quotation_price_configurator import get_lbracket_qty, get_zclip_qty
from datetime import timedelta


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
            columns += [_("Status") + ":text:105"]
            columns += [_("Qty Panel") + ":text:90"]
            columns += [_("Total Width") + ":text:90"]
            columns += [_("Qty LBracket") + ":text:90"]
            columns += [_("Qty ZClip") + ":text:90"]
            columns += [_("Qty Wallmount Kit") + ":text:90"]
            columns += [_("Ready for production") + ":date:105"]
            columns += [_("CNC") + ":text:60"]
            columns += [_("Paint") + ":text:60"]
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
            sales_order_list = frappe.db.get_all('Sales Order',
                                                 {'project': project.name, 'status': ('NOT IN', 'Cancelled')}, 'name')
            for so in sales_order_list:
                sales_order_items = frappe.db.get_all('Sales Order Item',
                                                      {'parenttype': 'Sales Order', 'parent': so.name},
                                                      'prevdoc_docname')
                sales_order_items = {soi['prevdoc_docname']: soi for soi in sales_order_items}.values()
                for soi in sales_order_items:  # we might have 1 or 2 sales order, but the second one will only have sample, no panel
                    if soi.prevdoc_docname:
                        panels = frappe.db.get_all('Price Configurator Item',
                                                   {'parenttype': 'Quotation', 'parent': soi.prevdoc_docname},
                                                   ['height', 'width', 'qty', 'welding_qty', 'nb_panel_with_zclip',
                                                    'wallmount_kit_qty', 'panel_with_wallmount_lbracket'])
                        if panels:
                            measurement = frappe.db.get_value('Quotation', {'name': soi.prevdoc_docname}, 'measurement')
                            quote_panel_list.extend(panels)
                            break  # once we find a sales order item linked to a quote, we don't need to continue looking for another one, because it will link to the same quote anyway
            if quote_panel_list:
                task_name = frappe.db.get_all('Task', {'project': project.name, 'status': ('IN', 'Open, Working')},
                                              'subject', order_by='task_order asc')[0]['subject']
                panel_qty = sum([int(row['qty']) for row in quote_panel_list])
                total_width = sum([float(row['width']) for row in quote_panel_list])
                lbracket_qty = sum([int(get_lbracket_qty(row, measurement)) for row in quote_panel_list])
                zclip_qty = sum([int(get_zclip_qty(row, measurement)) for row in quote_panel_list])
                wallmount_kit_qty = sum([int(row['wallmount_kit_qty']) for row in quote_panel_list])
                ready_for_production_date = self.get_ready_for_production_date(project.ready_for_production_date)
                cnc_time = self.get_cnc_required_time(panel_qty)
                paint_time = self.get_paint_required_time(total_width)
                sublimation_time = self.get_sublimation_required_time(panel_qty)
                installation_hardware_time = self.get_installation_required_time(panel_qty)
                inspection_time = self.get_inspection_required_time(panel_qty)
                tuple_obj = self.convert_to_tuple_obj(project.name, task_name, panel_qty, total_width, lbracket_qty,
                                                      zclip_qty, wallmount_kit_qty, ready_for_production_date, cnc_time,
                                                      paint_time,
                                                      sublimation_time, installation_hardware_time, inspection_time)
                tuple_list.append(tuple_obj)
        return tuple(tuple_list)  # data needs to be in Json

    def get_ready_for_production_date(self, ready_for_production_date):
        if self.filters['prj_type'] == 'Graphic':
            ready_for_production_date = ready_for_production_date + timedelta(days=35)
        return ready_for_production_date

    def convert_to_tuple_obj(self, project_name, task_name, panel_qty, total_width, lbracket_qty,
                             zclip_qty, wallmount_kit_qty, project_ready_for_production_date, cnc_time, paint_time,
                             sublimation_time, installation_hardware_time, inspection_time):
        obj = (project_name, task_name, panel_qty, total_width, lbracket_qty,
               zclip_qty, wallmount_kit_qty, project_ready_for_production_date, cnc_time, paint_time, sublimation_time,
               installation_hardware_time,
               inspection_time
               )
        return obj


    def get_cnc_required_time(self, panel_qty):
        return float(30 * panel_qty) / 60 #convert it into hours

    def get_paint_required_time(self, total_width):
        if total_width < 144:
            nb_min = 30
        else:
            nb_min = float(total_width/144) * 30
        return float("{0:.2f}".format(nb_min/60))

    def get_sublimation_required_time(self, panel_qty):
        return float(30 * panel_qty) / 60

    def get_installation_required_time(self, panel_qty):
        return float(panel_qty * 30) / 60

    def get_inspection_required_time(self, panel_qty):
        return float(panel_qty * 15) / 60

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
