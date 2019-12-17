# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext import get_default_currency
from frappe import _

class BankAccountSetup(Document):
	def validate(self):
		for dba in self.deposit_bank_account_list:
			if dba.currency != get_default_currency():
				dba.multi_currency = True
				if not dba.gain_lost_account:
					frappe.throw(_("You must enter a Gain Lost Account when the multi-currency is checked"))
