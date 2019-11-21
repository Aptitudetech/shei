#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
from frappe import _
import json
from six import string_types
from frappe.utils import cint, flt
from frappe.desk.notifications import get_filters_for

@frappe.whitelist(allow_guest=True)
def make_stock_entry():
    return 'test OKOK'

#@frappe.whitelist()
#def get_open_count(doctype, name, links):
#	'''Get open count for given transactions and filters
#	:param doctype: Reference DocType
#	:param name: Reference Name
#	:param transactions: List of transactions (json/dict)
#	:param filters: optional filters (json/list)'''
#
#
#	frappe.has_permission(doc=frappe.get_doc(doctype, name), throw=True)
#
#	meta = frappe.get_meta(doctype)
#
#	if isinstance(links, string_types):
#		links = json.loads(links, object_pairs_hook=frappe._dict)
#
#	# compile all items in a list
#	items = []
#	for group in links.transactions:
#		items.extend(group.get('items'))
#
#	out = []
#	for d in items:
#		if d in links.get('internal_links', {}):
#			# internal link
#			continue
#
#		filters = get_filters_for(d)
#		fieldname = links.get('non_standard_fieldnames', {}).get(d, links.fieldname)
#		#return fieldname
#		data = {'name': d}
#		if filters:
#			# get the fieldname for the current document
#			# we only need open documents related to the current document
#			filters[fieldname] = name
#			total = len(frappe.get_all(d, fields='name',
#				filters=filters, limit=100, distinct=True, ignore_ifnull=True))
#			data['open_count'] = total
#
#		total = len(frappe.get_all(d, fields='name',
#			filters={fieldname: name}, limit=100, distinct=True, ignore_ifnull=True))
#		data['count'] = total
#		out.append(data)
#
#	out = {
#		'count': out,
#	}
#
#	module = frappe.get_meta_module(doctype)
#	if hasattr(module, 'get_timeline_data'):
#		out['timeline_data'] = module.get_timeline_data(doctype, name)
#	
#	return out
#
##@frappe.whitelist()
##def get_open_count(doctype, name, links):
##	'''Get open count for given transactions and filters
##
##	:param doctype: Reference DocType
##	:param name: Reference Name
##	:param transactions: List of transactions (json/dict)
##	:param filters: optional filters (json/list)'''
##
##	frappe.has_permission(doc=frappe.get_doc(doctype, name), throw=True)
##
##	meta = frappe.get_meta(doctype)
#	
#	if isinstance(links, string_types):
#		links = json.loads(links, object_pairs_hook=frappe._dict)
#
#
#	# compile all items in a list
#	items = []
#	for group in links.transactions:
#		items.extend(group.get('items'))
#
#	out = []
#	for d in items:
#		if d in links.get('internal_links', {}):
#			# internal link
#			continue
#
#		filters = get_filters_for(d)
#		fieldname = links.get('non_standard_fieldnames', {}).get(d, links.fieldname)
#        #return fieldname
#		data = {'name': d}
#		if filters:
#			# get the fieldname for the current document
#			# we only need open documents related to the current document
#			filters[fieldname] = name
#			total = len(frappe.get_all(d, fields='name',
#				filters=filters, limit=100, distinct=True, ignore_ifnull=True))
#			data['open_count'] = total
#
#		total = len(frappe.get_all(d, fields='name',
#			filters={fieldname: name}, limit=100, distinct=True, ignore_ifnull=True))
#		data['count'] = total
#		out.append(data)
#
#	out = {
#		'count': out,
#	}
#
#	module = frappe.get_meta_module(doctype)
#	if hasattr(module, 'get_timeline_data'):
#		out['timeline_data'] = module.get_timeline_data(doctype, name)
#    
#	return out
#

#frappe.ui.form.on('Quotation', 'refresh', function(frm, cdt, cdn){
#	debugger;
#	if (!frm.doc.__islocal){
#		shei.dashboard_link_doctype(frm, 'Product Configurator', __('Sales Order'), {  //sales order = where the link should be displayed
#			'fieldname': 'quote',
#			'transactions': [
#				{
#					'items': ['Product Configurator'],
#					'label': __('Product Configurator')
#				}]
#		});
#	}
#});
#		/*if (!['Completed', 'Cancelled'].includes(frm.doc.status)){
#			frm.fields_dict.job_profile.grid.add_custom_button(__('Copy'), function(){
#				if (!(frm.fields_dict.job_profile.grid.get_selected()||[]).length){
#					frappe.msgprint(__('Select one line to copy!'));
#					return;
#				} else if ((frm.fields_dict.job_profile.grid.get_selected()||[]).length > 1){
#					frappe.msgprint(__('You can copy only one line per time!'));
#					return;
#				}
#				frm.fields_dict.job_profile.grid.get_selected_children().forEach(function(child){
#					child = frm.add_child('job_profile', child);
#					['3d_completed', 'drawing_number', '2d_due_date', '2d_accepted', '3d_due_date'].forEach((f) => {
#						frappe.model.set_value(child.doctype, child.name, f, null);
#					});
#					frm.refresh_field('job_profile');
#					frm.fields_dict.job_profile.grid.set_focus_on_row(child.idx);
#				});
#			});
#			frm.fields_dict.installation_profile.grid.add_custom_button(__('Copy'), function(){
#				if (!(frm.fields_dict.installation_profile.grid.get_selected()||[]).length){
#					frappe.msgprint(__('Select one line to copy!'));
#					return;
#				} else if ((frm.fields_dict.installation_profile.grid.get_selected()||[]).length > 1){
#					frappe.msgprint(__('You can copy only one line per time!'));
#					return;
#				}
#				frm.fields_dict.installation_profile.grid.get_selected_children().forEach(function(child){
#					child = frm.add_child('installation_profile', child);
#					frm.refresh_field('installation_profile');
#					frm.fields_dict.installation_profile.grid.set_focus_on_row(child.idx);
#				});
#			});
#		}
#	}
#});*/