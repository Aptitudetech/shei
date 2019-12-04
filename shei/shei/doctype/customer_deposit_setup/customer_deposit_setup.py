# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext import get_default_currency

class CustomerDepositSetup(Document):
	def validate(self):
		for dba in self.deposit_bank_account_list:
			if dba.currency != get_default_currency():
				dba.multi_currency = True

