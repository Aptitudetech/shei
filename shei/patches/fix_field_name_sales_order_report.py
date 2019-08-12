#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe

def execute():
	pass
#        for row in frappe.db.sql('select distinct name, json from `tabReport` WHERE is_standard=0 and ref_doctype = "Sales Order"', as_dict=1):
#                if not row.json: continue
#                data = json.loads(row.json)##

#                for k in ('height_in_mm', 'height_in_inches', 'width_in_mm', 'width_in_inches'):
#                        if k in data.get('column_widths', {}):
#                                data['column_widths'].pop(k)
#                        for field in data['fields'][:]:
#                                if k == field[0]:
#                                        data['fields'].remove(field)
#                if 'column_widths' in data:
#                        data['column_widths']['height'] = 50
#                        data['column_widths']['width'] = 50
#                        data['column_widths']['measurement'] = 20
#                if data.get('fields', []):
#                        data['fields'].insert(1, ['height', 'Sales Order Item'])
#                        data['fields'].insert(2, ['width', 'Sales Order Item'])
#                        data['fields'].insert(3, ['measurement', 'Sales Order Item'])
#                frappe.db.set_value('Report', row['name'], 'json', json.dumps(data), update_modified=False)
#        frappe.db.commit()







