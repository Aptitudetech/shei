#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import types
import json
import datetime
import unidecode
from datetime import timedelta
from datetime import datetime
from datetime import date
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, add_to_date, flt, now_datetime
from erpnext.accounts.utils import get_fiscal_year
from erpnext import get_default_currency
from erpnext.accounts.party import (get_party_account_currency)

@frappe.whitelist()
def on_project_before_save(doc_name,  proj_tasks=[]):
    doc = frappe.get_doc('Project', doc_name)
    curr_date = datetime.today().strftime('%m-%d-%Y')
    project_tasks = frappe.get_all('Project Task', fields=['*'], filters={ 'parenttype': 'Project', 'parent': doc.name })
    project_tasks.sort(key=order_task_by_name, reverse=False) #Need to order to be able to get the last closed task
    proj_tasks = json.loads( proj_tasks)
    proj_tasks.sort(key=order_task_by_name, reverse=False) #Need to order to be able to get the last closed task
    new_tasks = []
    end_time = None
    prev_task = None
    if proj_tasks and not project_tasks: #if there's something in the uI and nothing in the db
        for project_task in proj_tasks:
            project_task_status = frappe.db.get_value('Project Task', {'parent': doc.name, 'parenttype':'Project', 'title': project_task.title}, 'status')
            if not prev_task:
                project_task.start_date = doc.expected_start_date
            else:
                project_task.start_date, end_time = get_start_date_time(project_task.assigned_to, prev_task.end_date, end_time)
            task = frappe.db.get_value('Task', {'name': project_task.task_id}, '*')
            end_date, task_estimate_remaining_hour = get_next_valid_business_date_based_on_task_estimate(project_task['start_date'], task.assigned_to, task.expected_time, end_time)
            end_time = get_task_end_time_based_on_emp_schedules(task.assigned_to, end_date, task_estimate_remaining_hour)
            
            frappe.msgprint(_("start_date: {3}  --  end_date: {0}  --  task.expected_time:{1}  --  end_time: {2}  --  task_estimate_remaining_hour: {4}").format(end_date, task.expected_time, end_time, project_task.start_date, task_estimate_remaining_hour))
            
            project_task.end_date = end_date
            new_tasks.append(project_task) #then empty he list in UI and replace by this list
            prev_task = project_task
            #elif :
    else:
        index = 0
        for pro_task in proj_tasks:
            if pro_task['end_date'] != str(project_tasks[index]['end_date']): # in the db, the date is a Date while in the UI, it's a string
                new_tasks.append(pro_task) #add the last modified element into the list

                end_date = pro_task['end_date']
                index = index + 1                
                remaining_project_tasks = proj_tasks[index:] #we want to loop over the element after the modified one
                for project_task in remaining_project_tasks:  #proj_tasks
                    if not prev_task:
                        project_task['start_date'] = end_date
                        curr_time = now_datetime()
                        modified_date = str(curr_time).split(' ')[0]
                        end_time = str(curr_time).split(' ')[1].split(':')[:-1]
                        end_time = timedelta(hours=11, minutes=00) #time as string, need to convert it to timedelta
###                        end_time = timedelta(hours=int(end_time[0]), minutes=int(end_time[1])) #time as string, need to convert it to timedelta
                    else:
                        project_task['start_date'], end_time = get_start_date_time(project_task['assigned_to'], prev_task['end_date'], end_time)
                    task = frappe.db.get_value('Task', {'name': project_task['task_id']}, '*')
                    end_date, task_estimate_remaining_hour = get_next_valid_business_date_based_on_task_estimate(project_task['start_date'], task.assigned_to, task.expected_time, end_time)
                    end_time = get_task_end_time_based_on_emp_schedules(task.assigned_to, end_date, task_estimate_remaining_hour)
                    frappe.msgprint(_("start_date: {3}  --  end_date: {0}  --  task.expected_time:{1}  --  end_time: {2}  --  task_estimate_remaining_hour: {4}").format(end_date, task.expected_time, end_time, project_task['start_date'], task_estimate_remaining_hour))
                    project_task['end_date'] = end_date
                    new_tasks.append(project_task) #then empty he list in UI and replace by this list
                    prev_task = project_task
                    frappe.msgprint(_("project_task: {0}  ---   ed: {1}").format(project_task['title'], project_task['end_date']))

                break
            else:
                new_tasks.append(pro_task)
                index = index + 1
                #frappe.msgprint(_("proj_tasks: {0}").format(proj_tasks['title'], proj_tasks['end_date']))

    doc.set("tasks", [])
    doc.set("tasks", new_tasks)
    
    frappe.msgprint(_("new_tasks: {0}").format(new_tasks))
    

def get_start_date_time(assigned_to, prev_task_end_date, end_time):
    schedules = get_employee_schedule_by_weekday(assigned_to, prev_task_end_date)
    if len(schedules) == 0:
        start_date = get_next_business_date(assigned_to, prev_task_end_date)
        start_time = get_employee_schedule_by_weekday(assigned_to, start_date)[0]['start_time']
        return start_date, start_time
    else:
        end_shift_gauge = timedelta(hours=1) #let an hour at the end of the shift to cleanup, finishup things, ...
        end_shift = schedules[-1]['end_time']
        if (end_shift - end_time) >= end_shift_gauge:
            return prev_task_end_date, end_time
        else:
            start_date = get_next_business_date(assigned_to, prev_task_end_date)
            start_time = get_employee_schedule_by_weekday(assigned_to, start_date)[0]['start_time']
            return start_date, start_time

def get_next_business_date(assigned_to, date):
    holidays = get_all_holidays_curr_year()
    date = datetime.strptime(str(date), '%Y-%m-%d').date()
    date = date + timedelta(days=1)
    schedules = get_employee_schedule_by_weekday(assigned_to, date)
    while (str(date) in holidays) or (len(schedules) == 0): 
        date = date + timedelta(days=1)
        schedules = get_employee_schedule_by_weekday(assigned_to, date)
    return date


def get_task_end_time_based_on_emp_schedules(assigned_to, end_date, remaining_hour):
    """Return the end time of a task based on the employee schedule for the given date"""
    schedules = get_employee_schedule_by_weekday(assigned_to, end_date)
    for schedule in schedules:
        if (schedule['start_time'] + remaining_hour) <= schedule['end_time']:####
            return remaining_hour +  schedule['start_time']
        else:
            remaining_hour = remaining_hour - (schedule['end_time'] - schedule['start_time'])

def get_employee_working_hour_for_given_day(emp_email, date):
    """Returns the number of hour an employee must work for a given day"""
    schedules = get_employee_schedule_by_weekday(emp_email, date)
    total_work_time = timedelta(hours=0, minutes=0)
    for schedule in schedules: 
        time = schedule['end_time'] - schedule['start_time']
        total_work_time = total_work_time + time
    return total_work_time

def convert_number_to_hour(number):
    """Convert a given number to hours: 7.25 = 7:15"""
    time = str(number).split('.')
    if len(time[1]) == 1: #if original nbr = 1.4, we want to keep the 4, but as a 40
        time[1] = int(int(time[1]) * 10 * 0.6) #the double in is used to remove the '.0' at the end of the number
    elif not time[1]: #if the number doesn't have minute, set it to 00
        time[1] == '00'
    else:
        time[1] = int(int(time[1]) * 0.6)
    return timedelta(hours=int(time[0]), minutes=time[1])

def convert_hour_to_number(hour):
    """Convert a given hour to a number: 7:15 = 7.25"""
    time = str(hour).split(':')[:-1]
    if len(time[1]) == 1: #if original nbr = 1:40, we want to keep the 4, but as a 40
        time[1] = str(int(int(time[1]) * 10 * 0.6)) #the double in is used to remove the '.0' at the end of the number
    else:
        time[1] = str(int(time[1]) * 100 / 60)
    return float('.'.join(time))

def get_remaining_working_hour(emp_working_hour, end_time, schedules=[]):
    """Calculate remaining time before"""
    for s in schedules:
        if end_time > s['start_time'] and end_time < s['end_time']:
            return emp_working_hour - (end_time - s['start_time'])
        emp_working_hour - (s['end_time'] - s['start_time'])

def get_next_valid_business_date_based_on_task_estimate(date, assigned_to, estimate, end_time):
    """Get the next business date based on the assigned_to and the remaining hour left"""
    holidays = get_all_holidays_curr_year()
    date = datetime.strptime(str(date), '%Y-%m-%d').date()
    schedules = get_employee_schedule_by_weekday(assigned_to, date)
    estimate_remaining_hour = estimate
    estimate_day = 1000 #need to rethink how to have a vaue here
    
    emp_working_hour = get_employee_working_hour_for_given_day(assigned_to, date)
    if end_time and emp_working_hour: #the working_hour for that day will be equal to the remaining time before the end of the day

        emp_working_hour = get_remaining_working_hour(emp_working_hour, end_time, schedules)

        #if end_time > schedules[0]['start_time']:
        #    emp_working_hour = emp_working_hour - (end_time - schedules[0]['start_time'])
        
    if emp_working_hour: #if emp works
        emp_working_hour = convert_hour_to_number(emp_working_hour)
        estimate_day = estimate_remaining_hour // emp_working_hour
    if estimate_day == 0 and emp_working_hour:
        convert_number_to_hour(estimate_remaining_hour)
        return date, estimate_remaining_hour
    elif estimate_day > 0 and emp_working_hour and  end_time != schedules[0]['start_time']:
        estimate_remaining_hour = estimate_remaining_hour - emp_working_hour
        date = get_next_business_date(assigned_to, date)
        schedules = get_employee_schedule_by_weekday(assigned_to, date)
    
    while (estimate_remaining_hour >= emp_working_hour):
        emp_working_hour = convert_hour_to_number(get_employee_working_hour_for_given_day(assigned_to, date))
        #if len(schedules) != 0:
        if estimate_remaining_hour >= emp_working_hour:
            estimate_day = estimate_remaining_hour // emp_working_hour
        else:
            break
        estimate_remaining_hour = estimate_remaining_hour - emp_working_hour        
        date = get_next_business_date(assigned_to, date)
    
    time = convert_number_to_hour(estimate_remaining_hour)
    return date, time

def get_all_holidays_curr_year():
    """Get all the holiday for the current year. Holiday also contains the weekends"""
    now = datetime.now()
    curr_year = now.year
    holidays = []
    holidays_json = frappe.db.get_all('Holiday', {'parenttype': 'Holiday List', 'parent': 'CANADIAN HOLIDAY LIST ' + str(curr_year)}, 'holiday_date')
    for h in holidays_json:
        holidays.append(str(h['holiday_date']))
    return holidays

def order_task_by_name(json_obj):
    """Sort given json by task title"""
    try:
        if json_obj['title'].split('-')[1] == '02' and json_obj['title'].split('-')[2] == 'B PREFLIGHT': #for Alto + Folia, there's 2 tasks with '02', but one have 'A' and the other 'B'
            return 2.5 #returning 2.5 specify the task comes after the task '02' and before the '03' task
        return int(json_obj['title'].split('-')[1]) #get the number inside the task title
    except KeyError:
        return 0

def get_employee_schedule_by_weekday(email, date):
    import calendar
    weekday = date.weekday()
    weekday_name = calendar.day_name[weekday].lower()  #'wednesday'
    employee_name = frappe.db.get_value('User', email, ['first_name', 'last_name'], as_dict = True)
    workstation = frappe.db.get_value('Employee', {'first_name':unidecode.unidecode(employee_name.first_name), 'last_name': unidecode.unidecode(employee_name.last_name)}, 'workstation')
    if not workstation: #Employee don't have a naming convention. Some of them use first_name and Last_name, other put everything into the first_name as 'last_name, first_name'
        emp_name = unidecode.unidecode(employee_name.last_name) + ', ' + unidecode.unidecode(employee_name.first_name)
        workstation = frappe.db.get_value('Employee', {'employee_name':emp_name}, 'workstation')
    working_time = frappe.db.get_all('Workstation Working Hour', fields=['start_time', 'end_time'], filters={ 'parenttype': 'Workstation', 'parent': workstation, weekday_name:True })
    working_time.sort(key=order_time_by_start_time, reverse=False) #order to know start time to end time in order
    return working_time

def order_time_by_start_time(json_obj):
    """Sort given json by start_time"""
    try:
        time_list = str(json_obj['start_time']).split(':')[:-1]
        return float('.'.join(time_list)) #return time as float. ie 12h30 = 12.30
    except KeyError:
        return 0


def get_dashboard_info(party_type, party):
	current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
	company = frappe.db.get_default("company") or frappe.get_all("Company")[0].name
	party_account_currency = get_party_account_currency(party_type, party, company)
	company_default_currency = get_default_currency() \
		or frappe.db.get_value('Company', company, 'default_currency')

	if party_account_currency == company_default_currency:
		total_field = "base_grand_total"
	else:
		total_field = "grand_total"

	doctype = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"

	info = {}
	for i, dates in enumerate(((current_fiscal_year.year_start_date, current_fiscal_year.year_end_date),
		      (add_to_date(current_fiscal_year.year_start_date, years=-1), 
		       add_to_date(current_fiscal_year.year_end_date, years=-1)))):
		billing = frappe.db.sql("""
		select sum({0})
		from `tab{1}`
		where {2}=%s and docstatus=1 and posting_date between %s and %s
		""".format(total_field, doctype, party_type.lower()), 
			(party, dates[0], dates[1]))

		if i == 0:
			info['billing_this_year'] = flt(billing[0][0]) if billing else 0
		else:
			info['billing_last_year'] = flt(billing[0][0]) if billing else 0

	total_unpaid = frappe.db.sql("""
		select sum(debit_in_account_currency) - sum(credit_in_account_currency)
		from `tabGL Entry`
		where party_type = %s and party=%s""", (party_type, party))
	
	info['currency'] = party_account_currency
	info['total_unpaid'] = flt(total_unpaid[0][0]) if total_unpaid else 0
	if party_type == "Supplier":
		info["total_unpaid"] = -1 * info["total_unpaid"]

	return info

def on_party_onload(doc, handler):
    doc.set_onload("dashboard_info", get_dashboard_info(doc.doctype, doc.name))


def on_customer_validate(doc, handler=None):
#    if doc.is_new() and not doc.lead_name:
#        frappe.throw('Sorry, you need to create a Lead first')
    if not doc.get('customer_code'):
        doc.customer_code = frappe.db.get_value(
            'Custom Series',
            {'name': 'Customer'},
            'series'
        )


def on_customer_after_insert( doc, handler=None ):
    if doc.customer_code:
        frappe.db.set_value(
            'Custom Series',
            {'name': 'Customer'},
            'series',
            doc.customer_code + 1
        )


@frappe.whitelist()
def get_credit_notes( doctype, party_type, party_name ):
    sql = """
    SELECT '{0}' as `reference_type`,
        `tab{0}`.name as `reference_name`,
        `tab{0}`.remarks as `remarks`,
        abs(`tab{0}`.outstanding_amount) as `credit_amount`,
        abs(`tab{0}`.outstanding_amount) as `allocated_amount`
    FROM `tab{0}`
    WHERE `tab{0}`.outstanding_amount < 0
        AND `tab{0}`.`{1}` = %s
    GROUP BY `tab{0}`.`name`
    """.format(doctype, party_type)
    return frappe.db.sql(sql, (party_name,), as_dict=True)


def on_sales_invoice_submit( doc, handler=None ):
    if doc.get("credits"):
        je = frappe.new_doc('Journal Entry').update({
            "voucher_type": "Journal Entry",
            "posting_date": doc.posting_date,
            "company": doc.company,
            "multi_currency": doc.currency != frappe.db.get_value("Company", doc.company, "default_currency")
        })
        d_or_c = doc.debit_to if doc.doctype == "Sales Invoice" else doc.credit_to
        party = "Customer" if doc.doctype == "Sales Invoice" else "Supplier"

        doc.total_credits = 0.0
        for row in doc.credits:
            doc.total_credits += row.allocated_amount
            je.append("accounts",{
                "account": d_or_c,
                "party_type": party,
                "party": doc.get( frappe.scrub(party) ),
                "debit_in_account_currency": row.allocated_amount,
		"exchange_rate": doc.conversion_rate,
                "reference_type": row.reference_type,
                "reference_name": row.reference_name
            })
        je.append("accounts", {
            "account": d_or_c,
            "party_type": party,
            "party": doc.get( frappe.scrub(party) ),
            "credit_in_account_currency": row.allocated_amount,
            "exchange_rate": doc.conversion_rate,
            "reference_type": doc.doctype,
            "reference_name": doc.name
        })
        try:
            je.run_method('validate')
        except:
            frappe.clear_messages()
	if je.accounts[0].debit != je.accounts[1].credit:
		debit = je.accounts[0].debit
		credit = je.accounts[1].credit
		je.append("accounts", {
			"account": frappe.db.get_value("Company", doc.company, "exchange_gain_loss_account"),
			"credit_in_account_currency": debit - credit if credit < debit else 0.0,
			"debit_in_account_currency": credit - debit if debit < credit else 0.0
		})
        je.save()
        je.submit()
        doc.db_set('debit_note', je.name, update_modified=False)


def before_sales_invoice_cancel( doc, handler=None ):
    if doc.get("debit_note"):
        je = frappe.get_doc("Journal Entry", doc.debit_note)
        je.flags.ignore_links = True
        je.cancel()

def on_sales_invoice_validate(doc, handler=None):
    if doc.is_new():
        has_delivery_note = any([item.delivery_note for item in doc.items])
        if not has_delivery_note and frappe.db.exists("SHEI_Settings", "SHEI_Settings"):
            settings = frappe.get_doc("SHEI_Settings", "SHEI_Settings")

            user_restriction = settings.get("restrictions",{
                "source_doctype": "Sales Order",
                "user": frappe.session.user
            })
            if user_restriction:
                frappe.throw("Yo 're not allowed to create invoices from here !") 

@frappe.whitelist()
#Create a work order from a sales order
def create_work_order(so_name = None, mfg_items = []):
    '''Copy data from sales order and create a work order based on those data'''
    import json
    items = []
    if not mfg_items:
        return None 
    json_items = json.loads(mfg_items)
    for item in json_items:
        if 'width_in_inches' in item:
            new_item = {
                "item_code": item["item_code"] ,
                "item_description": item["description"] ,
                "quantity": item["qty"] , 
                "width": item['width_in_inches'],
                "height": item['height_in_inches'],
                "measurement": 'Inches',
            }
        elif 'width_in_mm' in item:
            new_item = {
                "item_code": item["item_code"] ,
                "item_description": item["description"] ,
                "quantity": item["qty"] , 
                "width": item['width_in_mm'],
                "height": item['height_in_mm'],
                "measurement": 'MM',
            }
        else:
            new_item = {
                "item_code": item["item_code"] ,
                "item_description": item["description"] ,
                "quantity": item["qty"],
            }
        items.append(new_item)
    
    so  = frappe.db.get_value('Sales Order', so_name, ['delivery_date', 'project'], as_dict=True)
    work_order_name = "WO-" + so_name.split("-")[1]
    #If Work order is new, creat it, otherwhise update it
    if frappe.db.exists('SO Work Order', work_order_name):
        work_order = frappe.get_doc('SO Work Order', work_order_name)
    else:
        work_order = frappe.new_doc('SO Work Order')

    work_order.update({
		'work_order_number': work_order_name,
		'expected_ship_date': so.delivery_date,
		'project': so.project,
		'work_order_items': items,
	})
    work_order.flags.ignore_permissions = True
    work_order.save()

    sales_order_doc = frappe.get_doc('Sales Order', so_name)
    sales_order_doc.update({ 'work_order' : work_order_name})
    sales_order_doc.flags.ignore_permissions = True
    sales_order_doc.save()
    frappe.msgprint("The Work Order have been updated")


