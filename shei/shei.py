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


@frappe.whitelist()
def get_cheque_series(account):
	#frappe.msgprint(str(account))
	if frappe.db.exists("Cheque Series", account):
		cheque_series = frappe.db.get_value("Cheque Series", account, "cheque_series")
        	cheque_series = int(cheque_series) + 1
		frappe.client.set_value("Cheque Series", account, "cheque_series", int(cheque_series))
		#frappe.msgprint(str(cheque_series))	
		return str(cheque_series)
	else:
		return " "

@frappe.whitelist()
def get_project_adv_bill(project_name):
	total = 0.0
	for si in frappe.get_list("Sales Invoice", fields=["name", "net_total"], filters={"project": project_name, "docstatus": 1, "is_for_advance_payment": True}): 
		total = si.net_total
	return str(total)

@frappe.whitelist()
def get_project_adv_paid(project_name):
	total = 0.0
        for si in frappe.get_list("Sales Invoice", fields=["name", "net_total"], filters={"project": project_name, "status": "Paid", "docstatus": 1, "is_for_advance_payment": True}):
                total = si.net_total
        return str(total)
