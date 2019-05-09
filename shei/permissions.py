#-*- coding: utf-8 -*-

import frappe


def get_project_permissions_query_conditions(user):
    if not user:
        user = frappe.session.user
    return "(ifnull(`tabProject`.restricted_to_role, '') IN ('', '{0}'))".format("', '".join(frappe.get_roles(user)))