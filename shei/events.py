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
from frappe.utils import nowdate, add_to_date, flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext import get_default_currency
from erpnext.accounts.party import (get_party_account_currency)

def on_project_before_save(doc, handler=None):
    #from erpnext.projects.doctype.project.project import validate 0
    #https://github.com/frappe/erpnext/blob/fcd0556119faf389d80fca3652e7e4f0729ebb6d/erpnext/projects/doctype/project/project.py#L126
    curr_date = datetime.today().strftime('%m-%d-%Y')
    project_tasks = frappe.get_all('Project Task', fields=['*'], filters={ 'parenttype': 'Project', 'parent': doc.name })
    project_tasks.sort(key=order_task_by_name, reverse=False) #Need to order to be able to get the last closed task

    #get_next_valid_business_date_based_on_nb_days(doc.expected_end_date, "mmurray@shei.sh", 5)
    #get_employee_schedule_by_weekday('mmurray@shei.sh', 0)
    get_employee_working_hour_for_given_day('nlaperriere@shei.sh', 3)
    ##set_task_date_based_on_expected_start_date(doc.expected_start_date, tasks)
#    frappe.throw("OK")

    for project_task in project_tasks:
        project_task_status = frappe.db.get_value('Project Task', {'parent': doc.name, 'parenttype':'Project', 'title': project_task.title}, 'status')
        if not project_task.start_date:
            ##new project
            project_task.start_date = doc.expected_start_date
            frappe.msgprint(_("project_task: {0}").format(project_task))
            task = frappe.db.get_value('Task', {'name': project_task.task_id}, '*')
            frappe.msgprint(_("task: {0}").format(task))

            frappe.msgprint(_("task.expected_time: {0}").format(task.expected_time))

            task_estimate_day = task.expected_time // get_employee_working_hour_for_given_day(task.assigned_to, 4)
            task_estimate_remaining_hour = task.expected_time % get_employee_working_hour_for_given_day(task.assigned_to, 4)
            
            end_date = get_next_valid_business_date_based_on_nb_days(project_task.start_date, task.assigned_to, task_estimate_day)
            frappe.throw(_("S: {0}  --  E:{1}").format(project_task.start_date, end_date))
            #set_task_date_based_on_expected_start_date(expected_start_date, tasks)
        if project_task_status == 'Open' and task.status == 'Closed': #the task have been recently closed
            #i.end_date = curr_date
            frappe.msgprint(_("task: {0}").format(task.as_json()))


def set_task_date_based_on_expected_start_date(expected_start_date, tasks=[]):
    tasks[0].exp_start_date = expected_start_date
    for task in tasks:
        expected_time = task.expected_time
        start_date = task.exp_start_date
        end_date = task.exp_end_date

def get_employee_working_hour_for_given_day(emp_email, weekday):
    """Returns the number of hour an employee must work for a given day"""
    schedules = get_employee_schedule_by_weekday(emp_email, weekday)
    total_work_time = timedelta(hours=0, minutes=0)
    for s in schedules: 
        time = s['end_time'] - s['start_time']
        total_work_time = total_work_time + time
    return total_work_time

def update_task_date_based_on_other_task(previous_task, tasks=[]):
    pass

def get_next_valid_business_date_based_on_nb_days(date, assigned_to, nb_days):
    """Get the next business date based on the assigned_to"""
    working_day = 0
    holidays = get_all_holidays_curr_year()
    date = datetime.strptime(str(date), '%Y-%m-%d').date()
    schedules = get_employee_schedule_by_weekday(assigned_to, date.weekday())
    while (str(date) in holidays) or (len(schedules) == 0) or (working_day < nb_days): #if the day is holiday or if employee isn't working on that day
        frappe.msgprint(_("scheudle: {0}  --  working_day: {1}  --  ").format(schedules, working_day))
        date = date + timedelta(days=1)
        working_day = working_day + 1
        schedules = get_employee_schedule_by_weekday(assigned_to, date.weekday())
        frappe.msgprint(_("Len schedule: {0}").format(len(schedules)))
        frappe.msgprint(_("(str(date) in holidays): {0} or (len(schedules) == 0): {1} or (working_day < nb_days): {2}").format((str(date) in holidays), (len(schedules) == 0), (working_day < nb_days)))

    return date


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


##def is_valid_business_date(date, assigned_to):
##    """Look if date is a valid business day based on assigned_to"""
##    holidays = get_all_holidays_by_year(date.year)
##
##    if date in holidays or (date.weekday() == 4 and assigned_to):
##        return False
##    else:
##        if date.weekday() == 4:# and 
##            return True
##
##def in_between(now, start, end):
##    if start <= end:
##        return start <= now <= end
##    else: # over midnight e.g., 23:30-04:15
##        return start <= now or now <= end
##
##
##def is_time_in_schedule(time, schedules = []):
##    """Look if given time is between the time inside the schedule"""
##    from datetime import datetime, time
##    
###    for schedule in schedules:
##
##    print("night" if in_between(datetime.now().time(), time(23), time(4)) else "day")

def get_employee_schedule_by_weekday(email, weekday):
    import calendar
    weekday_name = calendar.day_name[weekday].lower()  #'wednesday'
    employee_name = frappe.db.get_value('User', email, ['first_name', 'last_name'], as_dict = True)
    frappe.msgprint(_("employee_name: {0}").format(employee_name))

    workstation = frappe.db.get_value('Employee', {'first_name':unidecode.unidecode(employee_name.first_name), 'last_name': unidecode.unidecode(employee_name.last_name)}, 'workstation')
    if not workstation: #Employee don't have a naming convention. Some of them use first_name and Last_name, other put everything into the first_name as 'last_name, first_name'
        emp_name = unidecode.unidecode(employee_name.last_name) + ', ' + unidecode.unidecode(employee_name.first_name)
        workstation = frappe.db.get_value('Employee', {'employee_name':emp_name}, 'workstation')
    
    frappe.msgprint(_("email: {0}, employee_name: {1}, workstation: {2}").format(email, employee_name, workstation))

    working_time = frappe.db.get_all('Workstation Working Hour', fields=['start_time', 'end_time'], filters={ 'parenttype': 'Workstation', 'parent': workstation, weekday_name:True })
    frappe.msgprint(_("wt: {0}, workstation: {1}, weekday_name: {2}").format(working_time, workstation, weekday_name))
    working_time.sort(key=order_time_by_start_time, reverse=False) #order to know start time to end time in order

    return working_time

def order_time_by_start_time(json_obj):
    """Sort given json by start_time"""
    try:
        time_list = str(json_obj['start_time']).split(':')[:-1]
        return float('.'.join(time_list)) #return time as float. ie 12h30 = 12.30
    except KeyError:
        return 0

def get_pause_in_schedule(schedules = []):
    pass

def get_task_end_date(estimate_days, start_day, assigned_to):
    """Find the valid end date of a task"""
    pass

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
                frappe.throw("You're not allowed to create invoices from here !") 

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



