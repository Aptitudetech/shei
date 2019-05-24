#-*- coding: utf-8 -*-

import frappe

def get_project_permissions_query_conditions(user):
    if not user:
        user = frappe.session.user
    return "(ifnull(`tabProject`.restricted_to_role, '') IN ('', '{0}'))".format("', '".join(frappe.get_roles(user)))
    
#def has_permission_to_report(doc, user):
#    if 'Project Manager' in frappe.get_roles(user) and frappe.session.user != "Administrator" and doc.name == "PM Only - First Open Task by Open Project":
#		reports = map(lambda p: p.for_value, frappe.get_all("User Permission", fields="for_value", filters={
#			'user': user,
#			'allow': 'Report'}))
#		if reports:
#			return doc.name in reports

