# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import types
import json
import datetime
from frappe import _
from frappe.utils import now_datetime
from frappe.email.doctype.email_template.email_template import get_email_template


def send_warning_email():
    curr_time = now_datetime().replace(hour=now_datetime().hour - 1)
    failed_email_queue = frappe.db.get_all('Email Queue', {'status':'Error', 'modified': ('>=', curr_time)}, ['name', 'error', 'sender'])
    for eq in failed_email_queue:
        doc = frappe.get_doc('Email Queue', eq.name)
        eq_recipient = frappe.db.get_all('Email Queue Recipient', {'parenttype': 'Email Queue', 'parent': eq.name},
                                               'recipient')

        frappe.sendmail(
            recipients="mraymond@aptitudetech.net",
            **get_email_template('Error while sending email', {'doc': doc, 'recipients': eq_recipient})
        )
    print(failed_email_queue)