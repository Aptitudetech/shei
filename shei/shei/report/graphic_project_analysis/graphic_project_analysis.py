# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt, cint
import datetime

class GraphicProjectAnalysis(object):

    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.validate_filters()
        self.filters = self.update_filters()

    def validate_filters(self):
        try:
            if self.filters['from_expected_start_date'] > self.filters['to_expected_start_date']:
                frappe.throw(_("From Date cannot be greater than To Date"))
        except KeyError:
            frappe.throw(_("You must enter a From Date and a To Date"))

    def update_filters(self):
        """we can't have the same name in the filters twice, so we need to reformat the filter
            to match the name of the field and the condition in the right document"""
        from_date = self.filters['from_expected_start_date']
        to_date = self.filters['to_expected_start_date']
        try:
            status = self.filters['status']
            return {'expected_start_date': ('between', (from_date, to_date)), 'status':status}
        except KeyError:
            return {'expected_start_date': ('between', (from_date, to_date))}

    def run(self, filters):
        columns = self.get_columns(filters)
        data = self.get_data(filters)
        chart = self.get_chart_data(columns, data)
        return columns, data, None, chart

    def get_columns(self, filters):
        columns = [_("Project") + ":Link/Project:250"]
        columns += [_("Project Name") + ":text:200"]
        columns += [_("Project Manager") + ":Link/User:150"]
        columns += [_("Status") + ":text:105"]
        columns += [_("SubType") + ":text:105"]
        columns += [_("Exp. Start Date") + ":date:90"]
        columns += [_("Deposit Date") + ":date:90"]
        columns += [_("Preflight") + ":text:225"]
        columns += [_("PDF Approval Date") + ":date:90"]
        columns += [_("Printing") + ":date:90"]
        columns += [_("Inspection") + ":date:90"]
        columns += [_("Preflight Time") + ":text:90"]
        columns += [_("Printing Time") + ":text:90"]
        columns += [_("Fabrication Time") + ":text:90"]
        columns += [_("Total Time") + ":text:90"]
        return columns

    def get_data(self, filters):
        tuple_list = []
        self.filters.update({'sub_type': ('IN', 'Folia, Alto')})
        projects = frappe.db.get_all('Project', self.filters, ['name', 'shei_project_name', 'status', 'sub_type', 'expected_start_date', 'project_manager'])
        for project in projects:
            project_tasks = frappe.db.get_all('Project Task', {'parenttype':'Project', 'parent':project.name}, '*')
            deposit_end_date = self.get_deposit_closed_date(project_tasks)
            preflight_end_date = self.get_preflight_closed_time(project_tasks)
            printing_end_date = self.get_printing_date(project_tasks)
            inspection_end_date = self.get_inspection_date(project_tasks)
            tuple_obj = self.convert_to_tuple_obj(project, deposit_end_date, preflight_end_date, printing_end_date, inspection_end_date)
            tuple_list.append(tuple_obj)
        return tuple(tuple_list)  # data needs to be in Json

    def convert_to_tuple_obj(self, project, deposit_end_date, preflight_end_date, printing_end_date, inspection_end_date):
        obj = (project.name, project.shei_project_name, project.project_manager, project.status, project.sub_type,
            project.expected_start_date, deposit_end_date, preflight_end_date, project.date_ready_for_production, printing_end_date,
            inspection_end_date, self.get_preflight_time(preflight_end_date, deposit_end_date),
            self.get_printing_time(printing_end_date, project.date_ready_for_production), self.get_fabrication_time(inspection_end_date, printing_end_date),
            self.get_total_time(inspection_end_date, project.expected_start_date),
        )
        return obj

    def get_preflight_time(self, preflight_end_date, deposit_end_date):
        if not preflight_end_date or not deposit_end_date:
            return ""
        return (preflight_end_date - deposit_end_date).days

    def get_printing_time(self, printing_end_date, pdf_approval_end_date):
        if not printing_end_date or not pdf_approval_end_date:
            return ""
        return (printing_end_date - pdf_approval_end_date).days

    def get_fabrication_time(self, inspection_end_date, printing_end_date):
        if not inspection_end_date or not printing_end_date:
            return ""
        return (inspection_end_date - printing_end_date).days

    def get_total_time(self, inspection_end_date, project_expected_start_date):
        if not inspection_end_date or not project_expected_start_date:
            return ""
        return (inspection_end_date - project_expected_start_date).days

    def get_deposit_closed_date(self, tasks=[]):
		if tasks:
			return tasks[0].end_date


    def get_preflight_closed_time(self, tasks=[]):
		for task in tasks:
			if task.title == "ALTO-02-B PREFLIGHT":
				return task.end_date


    def get_printing_date(self, tasks=[]):
        for task in tasks:
            if task.title == 'ALTO-06-PRINTING / INSPECTION':
                return task.end_date

    def get_inspection_date(self, tasks=[]):
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
    args = {}
    return GraphicProjectAnalysis(filters).run(args)
