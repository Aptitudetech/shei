# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    #frappe.throw("Im Here in make sales invoice!")
    if frappe.db.exists("SHEI_Settings", "SHEI_Settings"):
        settings = frappe.get_doc("SHEI_Settings", "SHEI_Settings")

        user_restriction = settings.get("restrictions",{
            "source_doctype": "Sales Order",
            "user": frappe.session.user
        })
        if user_restriction:
            #frappe.local.response.http_status_code = 500
            frappe.throw("You're not allowed to create invoices from here") 
    return make_sales_invoice(source_name, target_doc, ignore_permissions)       

@frappe.whitelist()
def make_mapped_doc(method, source_name, selected_children=None):
    from frappe.model.mapper import make_mapped_doc
    for hook in frappe.get_hooks("override_whitelisted_methods", {}).get(method, []):
        # override using the first hook
        method = hook
        break
    return make_mapped_doc(method, source_name, selected_children)

@frappe.whitelist()
def map_docs(method, source_names, target_doc=None):
    from frappe.model.mapper import map_docs
    for hook in frappe.get_hooks("override_whitelisted_methods", {}).get(method, []):
        # override using the first hook
        method = hook
        break
    return map_docs(method, source_names, target_doc)
