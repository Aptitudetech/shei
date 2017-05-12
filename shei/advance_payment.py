# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_account_for_advance_payment(origin_account):
	return str(frappe.db.get_value("Advance Payment Setup", {'origin_account':origin_account}, "destination_account"))

@frappe.whitelist()
def get_account_for_regulare_payment(destination_account):
	return str(frappe.db.get_value("Advance Payment Setup", {"destination_account":destination_account}, "origin_account"))

@frappe.whitelist()
def get_customer_from_project(project):
        return str(frappe.db.get_value("Project", {"name":project}, "customer"))
