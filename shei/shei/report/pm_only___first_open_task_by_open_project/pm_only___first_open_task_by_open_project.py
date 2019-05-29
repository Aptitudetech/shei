# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt, cint

class PMOnlyFirstOpenTaskbyOpenProject(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.filters.report_date = getdate(self.filters.report_date or nowdate())
		self.age_as_on = getdate(nowdate()) \
			if self.filters.report_date > getdate(nowdate()) \
			else self.filters.report_date

	def run(self, args):
		#party_naming_by = frappe.db.get_value(args.get("naming_by")[0], None, args.get("naming_by")[1])
		columns = self.get_columns(args)
		data = self.get_data(args)
		#frappe.msgprint('<pre>{0}</pre>'.format(frappe.as_json(data)))
		chart = self.get_chart_data(columns, data)
		return columns, data, None, chart

	def get_columns(self, args):
        	user_roles = frappe.get_roles(frappe.session.user)
        	columns = [_("Project") + ":Link/Project:250"]
        	columns += [_("Project Name") + ":text:250"]
        	columns += [_("Amount") + ":Currency:90"]
        	columns += [_("SubType") + ":text:105"]
        	columns += [_("Subject") + ":text:250"]
        	columns += [_("Task") + ":Link/Task:100"]
        	columns += [_("Status") + ":text:105"]
        	columns += [_("Exp. End Date") + ":date:90"]
        	if ('Projects Manager' in user_roles):
            		columns += [_("Absolute End Date") + ":date:90"]
        	columns += [_("Project Manager") + ":Link/User:150"]
       		columns += [_("Type") + ":text:105"]
        	columns += [_("Assigned To") + ":Link/User:150"]
        	return columns

	def get_data(self, args):
		from erpnext.accounts.utils import get_currency_precision
		currency_precision = get_currency_precision() or 2
		company_currency = frappe.db.get_value("Company", self.filters.get("company"), "default_currency")
        	user_roles = frappe.get_roles(frappe.session.user)
        	if ('Projects Manager' in user_roles):
            		data = frappe.db.sql("""SELECT
                		tabProject.name,
                		tabProject.shei_project_name,
                		tabProject.project_amount_from_so,
                		tabProject.sub_type,
                		tabTask.subject,
                		tabTask.name,
                		tabTask.status,
                		tabProject.expected_end_date,
                		tabProject.absolute_end_date,
                		tabProject.project_manager,
                		tabProject.type,
                		tabTask.assigned_to
                		FROM tabProject
                		LEFT OUTER JOIN tabTask
                		    ON tabProject.name = tabTask.project
                		WHERE tabTask.status <> 'Closed'
                		AND tabProject.status = 'Open'
                		OR tabProject.status = 'Project Without Orders'
                		GROUP BY tabProject.name""")
        	else:
        	    data = frappe.db.sql("""SELECT
                	tabProject.name,
                	tabProject.shei_project_name,
                	tabProject.project_amount_from_so,
                	tabProject.sub_type,
                	tabTask.subject,
               	 	tabTask.name,
                	tabTask.status,
                	tabProject.expected_end_date,
                	tabProject.project_manager,
                	tabProject.type,
                	tabTask.assigned_to
                	FROM tabProject
                	LEFT OUTER JOIN tabTask
                	    ON tabProject.name = tabTask.project
                	WHERE tabTask.status <> 'Closed'
                	AND tabProject.status = 'Open'
                	OR tabProject.status = 'Project Without Orders'
                	GROUP BY tabProject.name""")
		return data

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
	return PMOnlyFirstOpenTaskbyOpenProject(filters).run(args)
