# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import json
import datetime
import unidecode
from datetime import timedelta
from datetime import datetime
from datetime import date
from frappe import _
from frappe.utils import nowdate, add_to_date, flt, now_datetime
from erpnext.accounts.utils import get_fiscal_year
from erpnext import get_default_currency
from erpnext.accounts.party import get_party_account_currency, _get_party_details
from quotation_price_configurator import convert_measurement_to_foot, calculate_welding_price, get_lbracket_qty, \
    get_single_additional_preflight_price, validate, get_zclip_qty, get_studs_price, get_av_nuts_price, \
    get_tools_price, get_folds_price, get_holes_price, calculate_zclip_price, get_lbracket_price, \
    get_wallmount_kit_price, get_preflight_price, get_technical_drawing_price, get_sample_without_order_price, \
    get_sample_with_order_price, get_graphic_design_price, get_color_match_price, get_matching_mural_price
from multilingual_extension.get_terms_and_conditions import get_terms_and_conditions


def on_request_for_quotation_validate(doc, handler=""):
    for item in doc.items:
        mr_item_prj = frappe.db.get_value('Material Request Item',
                                          {'parenttype': 'Material Request', 'parent': item.material_request,
                                           'item_code': item.item_code}, 'project')
        if mr_item_prj:
            item.project_name = mr_item_prj


def on_quotation_submit(doc, handler=""):
    for panel in doc.panel_list:
        cut_details = frappe.db.get_value('Dropdown Options',
                                          {'doctype_type': 'Price Configurator Item', 'variable_name': 'cut',
                                           'option_label': panel.cut}, '*')
        if cut_details.is_value_from_user and panel.outsource_amount == 0:
            frappe.throw(
                _("You must enter a valid amount for the outsourced cut. panel id: {0}").format(panel.panel_id))

def validate_term_condition_on_quote(doc):
    tc = get_terms_and_conditions(doc.party_name, doc.quotation_to)
    if tc != doc.tc_name:
        frappe.msgprint(_("There's a difference in the terms and condition! <br> the one you're using: {0} <br> "
                          "The one the system found: {1}").format(doc.tc_name, tc), indicator='orange',
                        title=_('Warning'))
    tax_template = _get_party_details(party=doc.party_name, party_type=doc.quotation_to,
                                      price_list=doc.selling_price_list,
                                      posting_date=doc.transaction_date,
                                      currency=doc.currency, company=doc.company, doctype="Quotation")
    if tax_template['taxes_and_charges'] != doc.taxes_and_charges:
        frappe.msgprint(_(
            "There's a difference in the taxes and charges! <br> the one you're using: {0} <br> The one the system found: {1}").format(
            doc.taxes_and_charges, tax_template['taxes_and_charges']), indicator='orange', title=_('Warning'))


def on_quotation_validate(doc, handler=None):
    if doc.quotation_mode == 'Price Configurator':
        set_default_value_pc(doc)
        validate(doc)
    validate_term_condition_on_quote(doc)

def set_default_value_pc(doc):
    for panel in doc.panel_list:
        if not panel.welding_qty:
            panel.welding_qty = 0
        if not panel.nb_panel_with_zclip:
            panel.nb_panel_with_zclip = 0
        if not panel.wallmount_kit_qty:
            panel.wallmount_kit_qty = 0
        if not panel.panel_with_wallmount_lbracket:
            panel.panel_with_wallmount_lbracket = 0
        if not panel.outsource_amount:
            panel.outsource_amount = 0
        if not panel.thickness:
            panel.thickness = "Alto 1/8"

def clear_item(doc):
    items = doc.get('items', [])
    doc.set('items', [])
    for item in items:
        if not item.reference_panel:
            doc.append('items', item)


def on_quotation_before_save(doc, handler=None):
    if doc.quotation_mode == 'Price Configurator':
        clear_item(doc)
        create_panel_items(doc)
        create_other_item(doc)
        create_graphical_item(doc)
        update_doc_totals(doc)
    for idx, item in enumerate(doc.items, 1):
        item.idx = idx
    doc.run_method('set_missing_values')
    doc.run_method('set_missing_item_details')
    doc.run_method('calculate_taxes_and_totals')


def add_item_to_list(doc, item_code, item_name, base_rate, qty, panel_id="", height="", width=""):
    '''Convert the given information into an item and append it to items list'''
    uom_details = frappe.db.get_value('UOM Conversion Detail',
                                      {'parenttype': 'Item', 'parent': item_code},
                                      ['uom', 'conversion_factor'], as_dict=True)
    warehouse = frappe.db.get_value('Item Default', {'parenttype': 'Item', 'parent': item_code},
                                    'default_warehouse')
    description = frappe.db.get_value('Item', item_code, 'description')
    measurement = ""
    if height or width:
        measurement = doc.measurement
    doc.append('items', {
        'item_code': item_code,
        'item_name': item_name,
        'description': description,
        'height': height or "",
        'width': width or "",
        'measurement': measurement,
        'qty': qty,
        'uom': uom_details['uom'],
        'conversion_factor': uom_details['conversion_factor'],
        'base_rate': base_rate,
        'warehouse': warehouse,
        'reference_panel': panel_id,
        'base_amount': base_rate * qty,
        'rate': float(base_rate) * (1 / doc.conversion_rate),
        'amount': float(base_rate) * qty * (1 / doc.conversion_rate),
    })


def create_other_item(doc):
    if doc.total_studs:
        studs_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'studs_item')
        unit_price = get_studs_price()
        add_update_quotation_item(doc, studs_item, studs_item, unit_price, doc.total_studs)
    if doc.total_av_nuts:
        nuts_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'nuts_item')
        price = get_av_nuts_price()
        add_update_quotation_item(doc, nuts_item, nuts_item, price, doc.total_av_nuts)
    if doc.total_tools:
        tool_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'tool_item')
        price = get_tools_price()
        add_update_quotation_item(doc, tool_item, tool_item, price, doc.total_tools)
    if doc.total_folds:
        folds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'folds_item')
        price = get_folds_price()
        add_update_quotation_item(doc, folds_item, folds_item, price, doc.total_folds)
    if doc.total_holes:
        holds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'holds_item')
        price = get_holes_price()
        add_update_quotation_item(doc, holds_item, holds_item, price, doc.total_holes)


def create_graphical_item(doc):
    # we always charge 1 preflight
    preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                         'preflight_item')
    price = get_preflight_price()
    add_update_quotation_item(doc, preflight_item, preflight_item, price, 1)
    if doc.have_matching_mural:
        matching_mural_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                  'matching_mural_item')
        price = get_matching_mural_price()
        add_update_quotation_item(doc, matching_mural_item, matching_mural_item, price, 1)  # we only charge it once
    if doc.need_colour_match:
        colour_match_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                'colour_match_item')
        price = get_color_match_price()
        add_update_quotation_item(doc, colour_match_item, colour_match_item, price, doc.nb_colour_to_match)
    if doc.have_graphic_design:
        graphic_design_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                  'graphic_design_item')
        price = get_graphic_design_price()
        add_update_quotation_item(doc, graphic_design_item, graphic_design_item, price, doc.graphic_design_nb_hours)
    if doc.sample_with_order_qty:
        sample_with_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                     'sample_with_order_item')
        price = get_sample_with_order_price()
        add_update_quotation_item(doc, sample_with_order_item, sample_with_order_item, price, doc.sample_with_order_qty)
    if doc.sample_without_order_qty:
        sample_without_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                        'sample_without_order_item')
        price = get_sample_without_order_price()
        add_update_quotation_item(doc, sample_without_order_item, sample_without_order_item, price,
                                  doc.sample_without_order_qty)
    if doc.have_technical_drawing:
        technical_drawing_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                     'technical_drawing_item')
        price = get_technical_drawing_price()
        add_update_quotation_item(doc, technical_drawing_item, technical_drawing_item, price,
                                  doc.technical_drawing_hours)
    if doc.number_of_files > 1:
        additional_preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                        'additionnal_preflight_item')
        price = get_single_additional_preflight_price()
        additionnal_preflight = doc.number_of_files - 1  # the first one is the regular 'preflight'
        add_update_quotation_item(doc, additional_preflight_item, additional_preflight_item, price,
                                  additionnal_preflight)


def update_doc_totals(doc):
    doc.total_qty = sum(float(i.qty) for i in doc.items)
    doc.base_total = sum(float(i.base_amount) for i in doc.items)  # cad
    doc.total = sum(float(i.amount) for i in doc.items)  # usd


def set_panel_sqft(doc, panel):
    panel.sqft_per_panel = convert_measurement_to_foot(panel.height, doc.measurement) * convert_measurement_to_foot(
        panel.width, doc.measurement)


def create_panel_items(doc):
    for panel in doc.panel_list:
        set_panel_sqft(doc, panel)
        create_aluminum_item(doc, panel)
        create_back_item(doc, panel)
        create_cut_item(doc, panel)
        create_thickness_item(doc, panel)
        create_welding_item(doc, panel)
        create_zclip_item(doc, panel)
        create_wallmount_item(doc, panel)
        create_wallmount_lbracket(doc, panel)


def create_welding_item(doc, panel):
    if panel.welding_qty:
        welding_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                           'welding_item')
        price = calculate_welding_price()
        add_update_quotation_item(doc, welding_item, welding_item, price, panel.welding_qty, panel.panel_id)


def create_wallmount_item(doc, panel):
    if panel.wallmount_kit_qty:
        wallmount_kit_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                 'wallmount_kit_item')
        price = get_wallmount_kit_price(panel, doc.measurement)
        add_update_quotation_item(doc, wallmount_kit_item, wallmount_kit_item, price, panel.wallmount_kit_qty,
                                  panel.panel_id)


def create_wallmount_lbracket(doc, panel):
    if panel.panel_with_wallmount_lbracket:
        lbracket_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                            'wallmount_lbracket_item')
        price = get_lbracket_price(panel, doc.measurement)
        lbracket_qty = get_lbracket_qty(panel, doc.measurement)
        add_update_quotation_item(doc, lbracket_item, lbracket_item, price, lbracket_qty, panel.panel_id)


def create_zclip_item(doc, panel):
    if panel.nb_panel_with_zclip:
        zclip_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'zclip_item')
        zclip_qty = get_zclip_qty(panel, doc.measurement)
        zclip_price = calculate_zclip_price(panel, doc.measurement)
        add_update_quotation_item(doc, zclip_item, zclip_item, zclip_price, zclip_qty, panel.panel_id)


def add_update_quotation_item(doc, item_code, item_name, base_rate, qty, panel_id="", height="", width=""):
    found = False
    for item in doc.items:
        if item.item_code == item_code and item.reference_panel == panel_id:
            if item.base_rate != base_rate or item.height != height or item.width != width or item.qty != qty:
                item.base_rate = base_rate
                item.qty = qty
                item.height = height
                item.width = width
            found = True
            break
    if not found:
        add_item_to_list(doc, item_code, item_name, base_rate, qty, panel_id, height, width)


def create_back_item(doc, panel):
    back_details = frappe.db.get_value('Dropdown Options',
                                       {'doctype_type': 'Price Configurator Item', 'variable_name': 'back',
                                        'option_label': panel.back}, '*')
    back_price = float(back_details.option_value)
    if back_details.is_calculated_with_uom:
        if back_details.uom.lower() == 'square foot':
            back_price = float(back_details.option_value) * panel.sqft_per_panel
    add_update_quotation_item(doc, back_details.related_item, panel.back, back_price, panel.qty, panel.panel_id)


def create_thickness_item(doc, panel):
    thickness_details = frappe.db.get_value('Dropdown Options',
                                            {'doctype_type': 'Price Configurator Item', 'variable_name': 'thickness',
                                             'option_label': panel.thickness}, '*')
    thickness_rate = float(thickness_details.option_value) * panel.sqft_per_panel
    add_update_quotation_item(doc, thickness_details.related_item, panel.thickness, thickness_rate, panel.qty,
                              panel.panel_id)


def create_cut_item(doc, panel):
    cut_details = frappe.db.get_value('Dropdown Options',
                                      {'doctype_type': 'Price Configurator Item', 'variable_name': 'cut',
                                       'option_label': panel.cut}, '*')
    if cut_details.is_value_from_user:
        cut_price = (panel.outsource_amount * 0.3) + panel.outsource_amount
        qty = 1
    else:
        cut_price = float(cut_details.option_value)
        qty = panel.qty
    add_update_quotation_item(doc, cut_details.related_item, panel.cut, cut_price, qty, panel.panel_id)


def create_aluminum_item(doc, panel):
    item_price = frappe.db.get_value('Item Price',
                                     {'price_list': 'Standard Selling', 'item_code': panel.aluminum_item},
                                     'price_list_rate')
    base_price = item_price * panel.sqft_per_panel
    add_update_quotation_item(doc, panel.aluminum_item, "Aluminum", base_price, panel.qty, panel.panel_id, panel.height,
                              panel.width)


def on_task_before_save(doc, handler=None):
    if not doc.is_new():
        return
    depends_on_task_subject_name = frappe.db.get_all('Dynamic Task Subject',
                                                     {'parent': doc.subject, 'parenttype': 'Task Template'},
                                                     'doctype_id')
    for ts in depends_on_task_subject_name:
        task = frappe.db.get_value('Task', {'project': doc.project, 'subject': ts.doctype_id}, 'name')
        doc.append('depends_on', {
            'task': task,
            'subject': ts.doctype_id,
            'project': doc.project,
            'description': doc.description,
        })


def on_issue_before_save(doc, handler=None):
    if doc.kanban_status == 'Completed' and frappe.db.get_value('Issue', doc.name, 'kanban_status') != 'Completed':
        doc.release_date = frappe.utils.nowdate()


def on_project_onload(doc, handler=None):
    doc.set("tasks", [])
    i = 1
    fields = ["title", "status", "start_date", "end_date", "description", "task_weight", "task_id"]
    exclude_fieldtype = ["Button", "Column Break",
                         "Section Break", "Table", "Read Only", "Attach", "Attach Image", "Color", "Geolocation",
                         "HTML", "Image"]

    custom_fields = frappe.get_all("Custom Field", {"dt": "Project Task",
                                                    "fieldtype": ("not in", exclude_fieldtype)}, "fieldname")

    for d in custom_fields:
        fields.append(d.fieldname)
    if doc.get('name'):
        doc.tasks = []
        i = 1
        for task in frappe.get_all('Task', '*', {'project': doc.name}, order_by='`task_order` asc'):
            task_map = {
                "title": task.subject,
                "status": task.status,
                "start_date": task.exp_start_date,
                "end_date": task.exp_end_date,
                "task_id": task.name,
                "description": task.description,
                "task_weight": task.task_weight,
                "idx": task.task_order or i
            }
            i += 1
            doc.map_custom_fields(task, task_map, custom_fields)

            doc.append("tasks", task_map)


# doc.is_new()
def update_project_status(task_title):
    if task_title == 'FOLIA-00-DEPOSIT' or task_title == 'ALTO-00-DEPOSIT':
        status = 'Deposit'
    if task_title == 'FOLIA-02-A WAITING FOR FILE' or task_title == 'ALTO-02-A WAITING FOR FILE':
        status = 'File'
    if task_title == 'FOLIA-02-B PREFLIGHT' or task_title == 'ALTO-02-B PREFLIGHT':
        status = 'Preflight'
    if task_title == 'FOLIA-03-DRAWING TECHICAL' or task_title == 'ALTO-03-DRAWING TECHICAL':
        status = 'PDF'
    if task_title == 'FOLIA-07-MATERIAL ORDERING' or task_title == 'ALTO-09-DEBURRING-CLEANING-PAINTING':
        status = 'Production'
    if task_title == 'FOLIA-04-SAMPLE PREPARATION' or task_title == 'ALTO-04-SAMPLE PREPARATION':
        status = 'Sample'
    if task_title == 'FOLIA-12-INSPECTION / PACKAGING' or task_title == 'ALTO-12-INSPECTION / PACKAGING':
        status = 'Ship'
    frappe.msgprint(_("status: {0}").format(status))
    return status


def get_last_open_project(kanban_task_status, project_tasks=[]):
    if kanban_task_status == 'On Hold':
        return 'On Hold'
    for task in project_tasks:
        if task.status == 'Open':
            return update_project_status(task.title)  # the next open task is the task after this one


def test(doc, handler=None):  # on_project_before_save
    if doc.is_new() or doc.sub_type not in ['Alto', 'Folia']:
        return
    curr_date = datetime.today().strftime('%m-%d-%Y')
    project_tasks = frappe.get_all('Project Task', fields=['*'], filters={'parenttype': 'Project', 'parent': doc.name})
    project_tasks.sort(key=order_task_by_name, reverse=False)  # Need to order to be able to get the last closed task
    # doc.kanban_task_status = get_last_open_project(doc.kanban_task_status, project_tasks)
    proj_tasks = []
    for pt in doc.get('tasks'):
        obj = json.loads(pt.as_json())
        proj_tasks.append(obj)
    proj_tasks.sort(key=order_task_by_name, reverse=False)  # Need to order to be able to get the last closed task
    new_tasks = []
    end_time = None
    prev_task = None
    if proj_tasks and not project_tasks:  # if there's something in the uI and nothing in the db
        for project_task in proj_tasks:
            project_task_status = frappe.db.get_value('Project Task', {'parent': doc.name, 'parenttype': 'Project',
                                                                       'title': project_task.title}, 'status')
            if not prev_task:
                project_task.start_date = doc.expected_start_date
            else:
                project_task.start_date, end_time = get_start_date_time(project_task.assigned_to, prev_task.end_date,
                                                                        end_time)
            task = frappe.db.get_value('Task', {'name': project_task.task_id}, '*')
            end_date, task_estimate_remaining_hour = get_next_valid_business_date_based_on_task_estimate(
                project_task['start_date'], task.assigned_to, task.expected_time, end_time)
            end_time = get_task_end_time_based_on_emp_schedules(task.assigned_to, end_date,
                                                                task_estimate_remaining_hour)

            frappe.msgprint(_(
                "start_date: {3}  --  end_date: {0}  --  task.expected_time:{1}  --  end_time: {2}  --  task_estimate_remaining_hour: {4}").format(
                end_date, task.expected_time, end_time, project_task.start_date, task_estimate_remaining_hour))

            project_task.end_date = end_date
            new_tasks.append(project_task)  # then empty he list in UI and replace by this list
            prev_task = project_task
            # elif :
    else:
        index = 0
        for pro_task in proj_tasks:
            if pro_task['end_date'] != str(
                    project_tasks[index]['end_date']):  # in the db, the date is a Date while in the UI, it's a string
                ##doc.kanban_task_status = update_project_status(project_tasks[index+1]['title'], doc.kanban_task_status, doc.name) #the next open task is the task after this one
                new_tasks.append(pro_task)  # add the last modified element into the list

                end_date = pro_task['end_date']
                index = index + 1
                remaining_project_tasks = proj_tasks[index:]  # we want to loop over the element after the modified one
                for project_task in remaining_project_tasks:  # proj_tasks
                    if not prev_task:
                        project_task['start_date'] = end_date
                        curr_time = now_datetime()
                        modified_date = str(curr_time).split(' ')[0]
                        end_time = str(curr_time).split(' ')[1].split(':')[:-1]
                        end_time = timedelta(hours=11, minutes=00)  # time as string, need to convert it to timedelta
                    ###                        end_time = timedelta(hours=int(end_time[0]), minutes=int(end_time[1])) #time as string, need to convert it to timedelta
                    else:
                        project_task['start_date'], end_time = get_start_date_time(project_task['assigned_to'],
                                                                                   prev_task['end_date'], end_time)
                    task = frappe.db.get_value('Task', {'name': project_task['task_id']}, '*')
                    end_date, task_estimate_remaining_hour = get_next_valid_business_date_based_on_task_estimate(
                        project_task['start_date'], task.assigned_to, task.expected_time, end_time)
                    end_time = get_task_end_time_based_on_emp_schedules(task.assigned_to, end_date,
                                                                        task_estimate_remaining_hour)
                    frappe.msgprint(_(
                        "start_date: {3}  --  end_date: {0}  --  task.expected_time:{1}  --  end_time: {2}  --  task_estimate_remaining_hour: {4}").format(
                        end_date, task.expected_time, end_time, project_task['start_date'],
                        task_estimate_remaining_hour))
                    project_task['end_date'] = end_date
                    new_tasks.append(project_task)  # then empty he list in UI and replace by this list
                    prev_task = project_task
                    # frappe.msgprint(_("project_task: {0}  ---   ed: {1}").format(project_task['title'], project_task['end_date']))
                break
            else:
                new_tasks.append(pro_task)
                index = index + 1
    doc.update({'tasks': new_tasks})


def get_start_date_time(assigned_to, prev_task_end_date, end_time):
    schedules = get_employee_schedule_by_weekday(assigned_to, prev_task_end_date)
    if len(schedules) == 0:
        start_date = get_next_business_date(assigned_to, prev_task_end_date)
        start_time = get_employee_schedule_by_weekday(assigned_to, start_date)[0]['start_time']
        return start_date, start_time
    else:
        end_shift_gauge = timedelta(hours=1)  # let an hour at the end of the shift to cleanup, finishup things, ...
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
        if (schedule['start_time'] + remaining_hour) <= schedule['end_time']:  ####
            return remaining_hour + schedule['start_time']
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
    if len(time[1]) == 1:  # if original nbr = 1.4, we want to keep the 4, but as a 40
        time[1] = int(int(time[1]) * 10 * 0.6)  # the double in is used to remove the '.0' at the end of the number
    elif not time[1]:  # if the number doesn't have minute, set it to 00
        time[1] == '00'
    else:
        time[1] = int(int(time[1]) * 0.6)
    return timedelta(hours=int(time[0]), minutes=time[1])


def convert_hour_to_number(hour):
    """Convert a given hour to a number: 7:15 = 7.25"""
    time = str(hour).split(':')[:-1]
    if len(time[1]) == 1:  # if original nbr = 1:40, we want to keep the 4, but as a 40
        time[1] = str(int(int(time[1]) * 10 * 0.6))  # the double in is used to remove the '.0' at the end of the number
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
    estimate_day = 1000  # need to rethink how to have a vaue here
    emp_working_hour = get_employee_working_hour_for_given_day(assigned_to, date)
    if end_time and emp_working_hour:  # the working_hour for that day will be equal to the remaining time before the end of the day
        emp_working_hour = get_remaining_working_hour(emp_working_hour, end_time, schedules)
    if emp_working_hour:  # if emp works
        emp_working_hour = convert_hour_to_number(emp_working_hour)
        estimate_day = estimate_remaining_hour // emp_working_hour
    if estimate_day == 0 and emp_working_hour:
        convert_number_to_hour(estimate_remaining_hour)
        return date, estimate_remaining_hour
    elif estimate_day > 0 and emp_working_hour and end_time != schedules[0]['start_time']:
        estimate_remaining_hour = estimate_remaining_hour - emp_working_hour
        date = get_next_business_date(assigned_to, date)
        schedules = get_employee_schedule_by_weekday(assigned_to, date)
    while (estimate_remaining_hour >= emp_working_hour):
        emp_working_hour = convert_hour_to_number(get_employee_working_hour_for_given_day(assigned_to, date))
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
    holidays_json = frappe.db.get_all('Holiday', {'parenttype': 'Holiday List',
                                                  'parent': 'CANADIAN HOLIDAY LIST ' + str(curr_year)}, 'holiday_date')
    for h in holidays_json:
        holidays.append(str(h['holiday_date']))
    return holidays


def order_task_by_name(json_obj):
    """Sort given json by task title"""
    try:
        if json_obj['title'].split('-')[1] == '02' and json_obj['title'].split('-')[
            2] == 'B PREFLIGHT':  # for Alto + Folia, there's 2 tasks with '02', but one have 'A' and the other 'B'
            return 2.5  # returning 2.5 specify the task comes after the task '02' and before the '03' task
        return int(json_obj['title'].split('-')[1])  # get the number inside the task title
    except KeyError:
        return 0


def get_employee_schedule_by_weekday(email, date):
    import calendar
    weekday = date.weekday()
    weekday_name = calendar.day_name[weekday].lower()  # 'wednesday'
    employee_name = frappe.db.get_value('User', email, ['first_name', 'last_name'], as_dict=True)
    workstation = frappe.db.get_value('Employee', {'first_name': unidecode.unidecode(employee_name.first_name),
                                                   'last_name': unidecode.unidecode(employee_name.last_name)},
                                      'workstation')
    if not workstation:  # Employee don't have a naming convention. Some of them use first_name and Last_name, other put everything into the first_name as 'last_name, first_name'
        emp_name = unidecode.unidecode(employee_name.last_name) + ', ' + unidecode.unidecode(employee_name.first_name)
        workstation = frappe.db.get_value('Employee', {'employee_name': emp_name}, 'workstation')
    working_time = frappe.db.get_all('Workstation Working Hour', fields=['start_time', 'end_time'],
                                     filters={'parenttype': 'Workstation', 'parent': workstation, weekday_name: True})
    working_time.sort(key=order_time_by_start_time, reverse=False)  # order to know start time to end time in order
    return working_time


def order_time_by_start_time(json_obj):
    """Sort given json by start_time"""
    try:
        time_list = str(json_obj['start_time']).split(':')[:-1]
        return float('.'.join(time_list))  # return time as float. ie 12h30 = 12.30
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

    # pydevd_pycharm.settrace('192.168.2.111', port=8005, stdoutToServer=True, stderrToServer=True)
    # frappe.errprint("allo")
    if not doc.get('customer_code'):
        doc.customer_code = frappe.db.get_value(
            'Custom Series',
            {'name': 'Customer'},
            'series'
        )


def on_customer_after_insert(doc, handler=None):
    if doc.customer_code:
        frappe.db.set_value(
            'Custom Series',
            {'name': 'Customer'},
            'series',
            doc.customer_code + 1
        )


def on_customer_before_save(doc, handler=None):
    if doc.is_new():
        pass
    address_name = frappe.db.get_value('Dynamic Link',
                               {'parenttype': 'Address', 'link_doctype': 'Customer', 'link_name': doc.name},
                               ['parent'])
    if address_name:
        country = frappe.db.get_value('Address', address_name, ['country'])
        if (doc.default_currency == 'USD' and country != 'United States') or (doc.default_currency == 'CAD' and country != 'Canada'):
            frappe.msgprint(_(
                "The country doesn't seems to match the currency. Please make sure the right currency have been enter"),
                            indicator='orange', title=_('Warning'))
    if not doc.shipping_address_name:
        frappe.msgprint(_(
            "The Quotation doesn't have a shipping address"),
            indicator='orange', title=_('Warning'))

@frappe.whitelist()
def get_credit_notes(doctype, party_type, party_name):
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


def on_sales_invoice_submit(doc, handler=None):
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
            je.append("accounts", {
                "account": d_or_c,
                "party_type": party,
                "party": doc.get(frappe.scrub(party)),
                "debit_in_account_currency": row.allocated_amount,
                "exchange_rate": doc.conversion_rate,
                "reference_type": row.reference_type,
                "reference_name": row.reference_name
            })
        je.append("accounts", {
            "account": d_or_c,
            "party_type": party,
            "party": doc.get(frappe.scrub(party)),
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


def before_sales_invoice_cancel(doc, handler=None):
    if doc.get("debit_note"):
        je = frappe.get_doc("Journal Entry", doc.debit_note)
        je.flags.ignore_links = True
        je.cancel()


def on_sales_invoice_validate(doc, handler=None):
    if doc.is_new():
        has_delivery_note = any([item.delivery_note for item in doc.items])
        if not has_delivery_note and frappe.db.exists("SHEI_Settings", "SHEI_Settings"):
            settings = frappe.get_doc("SHEI_Settings", "SHEI_Settings")

            user_restriction = settings.get("restrictions", {
                "source_doctype": "Sales Order",
                "user": frappe.session.user
            })
            if user_restriction:
                frappe.throw("You're not allowed to create invoices from here")


@frappe.whitelist()
def update_work_order(so_name=None, mfg_items=[], work_order_name=""):
    '''Update the latest Work Order related to the given Sales Order'''
    items = []
    if not mfg_items:
        return None
    if not work_order_name:
        frappe.throw(_("Please create a work order first"))
    json_items = json.loads(mfg_items)
    for item in json_items:
        new_item = {
            "item_code": item["item_code"],
            "item_description": item["description"],
            "quantity": item["qty"],
            "width": item.get('width', 0),
            "height": item.get('height', 0),
            "measurement": item.get('measurement', "")
        }
        items.append(new_item)

    so = frappe.db.get_value('Sales Order', so_name, ['delivery_date', 'project'], as_dict=True)
    work_order = frappe.get_doc('SO Work Order', work_order_name)
    work_order.update({
        'work_order_number': work_order_name,
        'expected_ship_date': so.delivery_date,
        'project': so.project,
        'work_order_items': items,
    })
    work_order.flags.ignore_permissions = True
    work_order.save()
    frappe.msgprint("The Work Order have been updated")


@frappe.whitelist()
def create_work_order(so_name=None, mfg_items=[]):
    '''Copy data from sales order and create a work order based on those data'''
    sales_order_doc = frappe.get_doc('Sales Order', so_name)
    work_order_name = "WO-" + "-".join(so_name.split('-')[1:])
    version = 1
    if len(sales_order_doc.work_orders) != 0:
        while frappe.db.exists('SO Work Order', work_order_name):
            work_order_name = "WO-" + ".".join(so_name.split('-')[1:]) + 'v' + str(version)
            version += 1
    work_order = frappe.new_doc('SO Work Order')
    work_order.work_order_number = work_order_name
    work_order.flags.ignore_permissions = True
    work_order.save()
    update_work_order(so_name, mfg_items, work_order.name)
    sales_order_doc.append('work_orders', {
        'link_doctype': 'SO Work Order',
        'link_name': work_order_name
    })
    sales_order_doc.flags.ignore_permissions = True
    sales_order_doc.save()
    frappe.msgprint("The Work Order have been created")
