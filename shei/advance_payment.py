# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_account_for_advance_payment(origin_account):
	
	#if customer_code == "" :
	#	frappe.msgprint("You must choose a customer first.")
	#	return ""
	#frappe.msgprint(str(frappe.db.get_value("Advance Payment Setup", {'origin_account':origin_account}, "destination_account")))
	#return str(str_save_file += frappe.db.get_value("Advance Payment Setup", {'origin_account':origin_account}, "destination_account"))
	return str(frappe.db.get_value("Advance Payment Setup", {'origin_account':origin_account}, "destination_account")) 
