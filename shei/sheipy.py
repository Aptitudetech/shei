# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def change_project_name(dt, project_name, customer_name):

        new_dt = ""
        if project_name.lower().startswith("proj-"):
                project_code = "(" + project_name[-5:] + ") " + customer_name
                new_dt = frappe.rename_doc(dt, project_name, project_code)
                pr = frappe.get_doc("Project", new_dt)
                pr.customer = customer_name
                pr.save()
        elif project_name.lower().startswith("("):
                new_name = project_name[:6]
                new_name = new_name[-5:]
                project_code = "(" + new_name + ") " + customer_name
                if project_code != project_name:
                        new_dt = frappe.rename_doc(dt, project_name, project_code)
                        pr = frappe.get_doc("Project", new_dt)
                        pr.customer = customer_name
                        pr.save()
        else:
                new_name = project_name[-6:]
                new_name = new_name[:-1]
                project_code = "(" + new_name + ") " + customer_name
                new_dt = frappe.rename_doc(dt, project_name, project_code)
                pr = frappe.get_doc("Project", new_dt)
                pr.customer = customer_name
                pr.save()

        return new_dt

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
def get_project_so(project_name):
        project_amount = 0.0
        for so in frappe.get_list("Sales Order", fields=["name", "net_total"], filters={"project": project_name, "docstatus": 1}):
                project_amount = project_amount + so.net_total
        return str(project_amount)

@frappe.whitelist()
def set_project_so():
	count = 0
        project_amount = 0.0
	for p in frappe.get_list("Project", fields="name", filters={"status": "Open"}):
	        for so in frappe.get_list("Sales Order", fields=["name", "net_total"], filters={"project": p.name , "docstatus": 1}):
        	        project_amount = project_amount + so.net_total
		frappe.client.set_value("Project", p.name, "project_amount_from_so", project_amount)
		project_amount = 0.0
		count = count + 1
	frappe.msgprint(str(count) + " Projects were updated")

@frappe.whitelist()
def set_project_customer_deposit(project_name):
        count = 0
	if project_name == "all":
		flt = {}
	else:
		flt = {"name": project_name}
        for i in frappe.get_list("Project", fields="name", filters=flt):
		pj = frappe.get_doc("Project", i.name)
		to_remove = []
		for i in pj.get('customer_deposit_item'):
			to_remove.append(i)
		[pj.remove(d) for d in to_remove]

		for i in frappe.get_list("Customer Deposit", fields="name", filters={"project": pj.name, "docstatus": 1}):
			cd = frappe.get_doc("Customer Deposit", i.name)
                        applied = False
                        if cd.customer_deposit_application:
                        	applied = True
			for i in cd.get('customer_deposit_quotation'):
				pj.append("customer_deposit_item", {
					"customer_deposit": cd.name,
					"deposit_invoice": i.quotation,
					"base_net_total": frappe.db.get_value("Quotation", {"name": i.quotation, "docstatus": 1}, "base_net_total"),
					"reception_date": cd.posting_date,
					"deposit_applied": applied
				})
		count = count + 1
		pj.save()
#	frappe.msgprint(str(count) + " Projects were updated")

