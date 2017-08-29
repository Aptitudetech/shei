#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe

def execute():
    start = frappe.db.get_value('Custom Series', {'name': 'Customer'}, 'series')
    if not start:
        frappe.new_doc('Custom Series').update({
            "type": "Customer",
            "series": 1000
        }).insert()
        start = 1000
    count = 0
    for name in frappe.db.sql('SELECT `name` FROM `tabCustomer` where ifnull(customer_code, "") = "" ORDER BY creation'):
        frappe.db.set_value(
            'Customer',
            name[0],
            'customer_code',
            start + count,
            update_modified = False
        )
        count += 1
    frappe.db.set_value('Custom Series', {'name': 'Customer'}, 'series', start + count)