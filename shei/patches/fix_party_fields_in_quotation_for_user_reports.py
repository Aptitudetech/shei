#-*- coding: utf-8 -*-

import json
import frappe

def execute():
	for row in frappe.db.sql('select distinct name, json from `tabReport` WHERE is_standard=0 and ref_doctype = "Quotation"', as_dict=1):
		if not row.json: continue
		data = json.loads(row.json)

		for k in ('lead', 'customer', 'customer_name'):

			if k in data.get('column_widths', {}):
				data['column_widths'].pop(k)

			for field in data['fields'][:]:
				if k == field[0]:
					data['fields'].remove(field)

			for _filter in data.get('filters', []):
				if k == _filter[1]:
					_filter[1] = 'party_name'

		if 'column_widths' in data:
			data['column_widths']['quotation_to'] = 78
			data['column_widths']['party_name'] = 128
			data['column_widths']['customer_name'] = 128

		if data.get('fields', []):
			data['fields'].insert(1, ['quotation_to', 'Quotation'])
			data['fields'].insert(2, ['party_name', 'Quotation'])
			data['fields'].insert(3, ['customer_name', 'Quotation'])

		frappe.db.set_value('Report', row['name'], 'json', json.dumps(data), update_modified=False)

	frappe.db.commit()
