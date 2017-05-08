# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def change_project_name(dt, project_name, customer_name):

#        cu = frappe.get_doc("Customer", customer_code)
#        item = frappe.get_doc("Item", item_code)
        project_code = customer_name + " (" + project_name[-5:] + ")"
        new_dt = frappe.rename_doc(dt, project_name, project_code)
#       frappe.msgprint(project_code)
        pr = frappe.get_doc("Project", new_dt)
        pr.customer = customer_name
        pr.save()

        return new_dt

