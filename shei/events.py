#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
from frappe.model.naming import make_autoname

def on_customer_validate(doc, handler=None):
    if not doc.get('customer_code'):
        doc.customer_code = frappe.db.get_value(
            'Custom Series',
            {'name': doc.name},
            'series'
        )

def on_customer_after_insert( doc, handler=None ):
    if doc.customer_code:
        frappe.db.set_value(
            'Custom Series',
            {'name': doc.name},
            'series',
            doc.customer_code + 1
        )
