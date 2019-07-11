# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt, cint

class GraphicProjectAnalysis(object):

	def __init__(self, filters=None):
                self.filters = frappe._dict(filters or {})
                self.filters.report_date = getdate(self.filters.report_date or nowdate())
                self.age_as_on = getdate(nowdate()) \
                        if self.filters.report_date > getdate(nowdate()) \
                        else self.filters.report_date

        def run(self, args):
                columns = self.get_columns(args)
                data = self.get_data(args)
                chart = self.get_chart_data(columns, data)
                return columns, data, None, chart

        def get_columns(self, args):
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

	def get_data(self, args):
                from erpnext.accounts.utils import get_currency_precision
                currency_precision = get_currency_precision() or 2
                company_currency = frappe.db.get_value("Company", self.filters.get("company"), "default_currency")
		projects = frappe.db.get_all('Project', {'status':'open'}, ['name', 'shei_project_name', 'status', 'sub_type', 'expected_start_date'])
		#deposit date, preflight, pdf approval, printing, inspection, preflight time, printing time, fabrication time, total time
		
                return tuple(data) #data needs to be in Json

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
        return GraphicProjectAnalysis(filters).run(args)
