# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import add_days, formatdate

@frappe.whitelist()
def update_terms():
        count = 0
        for i in frappe.get_list("Customer", fields="name"):
                cust = frappe.get_doc("Customer", i)
                tc = frappe.db.get_value("Terms and Conditions Multilingual Extension", {"customer_group": cust.customer_group, "language": cust.language}, "tc_name")
#               frappe.msgprint(tc)
                frappe.db.set_value("Customer", i, "tc_name", tc)
#               cust.terms_and_conditions = frappe.db.get_value("Terms and Conditions Multilingual Extension", {"customer_group": cust.customer_group, "language": cust.language}, "tc_name")
#               cust.save()
                count += 1
#               for i in frappe.get_list("Terms and Conditions Multilingual Extension", fields="tc_name", filters={"customer_group": cust.customer_group, "language": cust.language}):
        frappe.msgprint(str(count) + " " + "Customers were updated")

@frappe.whitelist()
def get_due_date(supplier, bill_date):
        due_date = formatdate(add_days(bill_date, frappe.db.get_value("Supplier", supplier, "credit_days")))
        return due_date

@frappe.whitelist()
def update_task_order(grid_tasks=[]):
	json_list = json.loads(grid_tasks)
	for t in json_list:
		frappe.msgprint("t: {0}".format(t))
#		if frappe.db.exists('Task', t['task_id']):
		try:
	                task = frappe.get_doc("Task", t['task_id'])
#		else:
#			task = frappe.new_doc('Task')
#		task.flags.ignore_permission = True
#		try:
#		        task.update({'subject': t['title'], 'assigned_to': t['assigned_to']})
#		except KeyError:
#		        task.update({'subject': t['title']})
		        task.update({'task_order': t['idx'], 'task_id': t['task_id']})
        	        task.save()
		except KeyError:
			pass
#	frappe.db.commit()

@frappe.whitelist()
def get_tasks_from_template(project_name):
        pj = frappe.get_doc("Project", project_name)
	task_subjects = frappe.db.get_all('Task Subject', {'disabled': False, 'sub_type': pj.sub_type}, '*')
	nb_rows = frappe.db.get_value('Task', {'project':pj.name}, 'task_order', order_by='task_order desc')
	for t in task_subjects:
		if nb_rows:
			task_order = t.task_order + int(nb_rows)
		else:
			task_order = t.task_order
        	json_update = {
                	"subject": t.name,
                        "status": 'Open',
                        "assigned_to": t.assigned_to,
                        "project": pj.name,
			"task_order": task_order,
		}
                task = frappe.new_doc("Task")
                task.update(json_update)
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
def on_project_onload(project_name):
	return get_project_so(project_name)

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

@frappe.whitelist()
def set_project_pfi(pfi, action):

        pfi = frappe.get_doc("Quotation", pfi)
        pj = frappe.get_doc("Project", pfi.project)
        if action == "add":
                pj.append("customer_deposit_item", {
                        "deposit_invoice": pfi.name,
                        "net_total": pfi.net_total,
                        "base_net_total": pfi.base_net_total,
                })
                pj.save()
        elif action == "remove":
                to_remove = []
                for i in pj.get('customer_deposit_item'):
                        if i.deposit_invoice == pfi.name:
                                to_remove.append(i)
                [pj.remove(d) for d in to_remove]
                pj.save()

@frappe.whitelist()
def fetch_items_from_so(so):

        item_so_dict = {}
        item_ste_dict = {}
        item_total_dict = {}

        so = frappe.get_doc("Sales Order", so)

        for s in frappe.get_list("Stock Entry", fields="name", filters={"sales_order": so.name, "docstatus": 1}):
                ste = frappe.get_doc("Stock Entry", s.name)
                for i in ste.get('items'):
                        if frappe.db.get_value("Item", {"item_code":i.item_code}, "is_stock_item"):
                                if not item_ste_dict.has_key(i.item_code):
                                        updateDict(i.item_code, i.qty, item_ste_dict)
                                else:
                                        qty = i.qty + item_ste_dict.get(i.item_code)
                                        updateDict(i.item_code, qty, item_ste_dict)

        for so_i in so.get('items'):
                if frappe.db.get_value("Item", {"item_code":so_i.item_code}, "is_stock_item") == True:
                        qty = 0
                        # passer à travers le dictionnaire pour voir si l'item est déjà présent
                        for k, v in item_so_dict.iteritems():
                                # si l'item est présent, additionner la quantité de l'item à la quantité existante
                                if k == so_i.item_code:
                                        qty = so_i.qty + v
                        # si l'item était déjà existant dans le dictionnaire, mettre à jour la quantité de cet item
                        if qty != 0:
                                updateDict(so_i.item_code, qty, item_so_dict)
                        # l'item n'était pas présent dans le dictionnaire, on ajoute un nouveau
                        else:
                                updateDict(so_i.item_code, so_i.qty, item_so_dict)

	if item_ste_dict:
		for so_k, so_v in item_so_dict.iteritems():
			for ste_k, ste_v in item_ste_dict.iteritems():
				if ste_k == so_k:
					ste_qty = so_v - ste_v
					if ste_qty != 0:
						updateDict(so_k, str(ste_qty), item_total_dict)
	else:
		item_total_dict = dict(item_so_dict)

        return item_total_dict

def updateDict(key, value, aDict):
        if not key in aDict:
                aDict[key] = value
        else:
                aDict.update({key: value})

