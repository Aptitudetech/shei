# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, formatdate

@frappe.whitelist()
def get_due_date(supplier, bill_date):

        due_date = formatdate(add_days(bill_date, frappe.db.get_value("Supplier", supplier, "credit_days")))

        return due_date

@frappe.whitelist()
def get_tasks_from_template(project_name):

        pj = frappe.get_doc("Project", project_name)
        for i in frappe.get_list("Project", fields="name", filters={"status": "Template", "sub_type": pj.sub_type}):
                pj_template = frappe.get_doc("Project", i.name)
                for i in frappe.get_list("Task", fields="name", filters={"project": pj_template.name}, order_by="subject"):
                        task_template = frappe.get_doc("Task", i.name)
                        json_update = {
                                "subject": task_template.subject,
                                "status": task_template.status,
                                "assigned_to": task_template.assigned_to,
                                "project": pj.name
                        }
                        task = frappe.new_doc("Task")
                        task.update (json_update)
                        task.save()

@frappe.whitelist()
def update_template_project():

        for i in frappe.get_list("Project", fields="name", filters={"status": "Open"}):
                pj = frappe.get_doc("Project", i.name)
                to_remove = []
                for i in pj.get('tasks'):
                        to_remove.append(i)
                [pj.remove(d) for d in to_remove]
                pj.save()

        count = 0
        for i in frappe.get_list("Project", fields="name", filters={"status": "Open"}):
                pj_open = frappe.get_doc("Project", i.name)
                for i in frappe.get_list("Project", fields="name", filters={"status": "Template", "sub_type": pj_open.sub_type}):
                        pj_template = frappe.get_doc("Project", i.name)
                        for i in frappe.get_list("Task", fields="name", filters={"project": pj_template.name}, order_by="subject"):
                                task_template = frappe.get_doc("Task", i.name)
                                json_update = {
                                        "subject": task_template.subject,
                                        "status": task_template.status,
                                        "assigned_to": task_template.assigned_to,
                                        "project": pj_open.name
                                }
                                task = frappe.new_doc("Task")
                                task.update (json_update)
                                task.save()
                count += 1

        frappe.msgprint("done " + str(count))

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
                if (get_digits(new_name)) == 3:
                        new_name = project_name[:4]
                        new_name = new_name[-3:]
                elif get_digits(new_name) == 4:
                        new_name = project_name[:5]
                        new_name = new_name[-4:]
                elif get_digits(new_name) == 5:
                        new_name = project_name[:6]
                        new_name = new_name[-5:]
                project_code = "(" + new_name + ") " + customer_name
                if project_code != project_name:
                        new_dt = frappe.rename_doc(dt, project_name, project_code)
                        pr = frappe.get_doc("Project", new_dt)
                        pr.customer = customer_name
                        pr.save()
        elif project_name.lower().endswith(")"):
                new_name = project_name[-6:]
                if (get_digits(new_name)) == 3:
                        new_name = new_name[-4:]
                        new_name = new_name[:3]
                elif get_digits(new_name) == 4:
                        new_name = new_name[-5:]
                        new_name = new_name[:4]
                elif get_digits(new_name) == 5:
                        new_name = new_name[-6:]
                        new_name = new_name[:5]
                project_code = "(" + new_name + ") " + customer_name
                new_dt = frappe.rename_doc(dt, project_name, project_code)
                pr = frappe.get_doc("Project", new_dt)
                pr.customer = customer_name
                pr.save()
        else:
                project_code = "(" + update_project_series() + ") " + customer_name
                new_dt = frappe.rename_doc(dt, project_name, project_code)
                pr = frappe.get_doc("Project", new_dt)
                pr.customer = customer_name
                pr.save()

        return new_dt

def update_project_series():
        s = frappe.get_doc("Custom Series", "Project")
        s.series += 1
        s.save()
        return str(s.series)

def get_digits(str1):
        c = ""
        for i in str1:
                if i.isdigit():
                        c += i
        return len(c)

@frappe.whitelist()
def get_sales_person_from_customer(dt, customer_name, project):
        cust = frappe.get_doc("Customer", customer_name)
        prj = frappe.get_doc("Project", project)
@frappe.whitelist()
def get_sales_person_from_customer(dt, customer_name, project):
        cust = frappe.get_doc("Customer", customer_name)
        prj = frappe.get_doc("Project", project)
        for i in cust.get('sales_team'):
                prj.sales_person = i.sales_person
        prj.save()

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

