# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CustomerDepositSetup(Document):
	
	def validate(self):
		currencies = ['None']
		for child in self.get('deposit_setting'):
			if child.account_currency not in currencies:
				currencies.append(child.account_currency)				
			else:
				frappe.throw("Sorry, you can only have each currencies once. <br> Problematic currency: {0}".format(child.account_currency))
			if child.account_currency != 'CAD':
				child.multi_currency = True

@frappe.whitelist()
def get_bank_account_by_currency(chosen_currency = None):
	banks = []
	bank_accounts = frappe.db.get_all('Bank Account', None)
	for ba in bank_accounts:
		account_name = frappe.db.get_value('Bank Account', ba['name'], 'account')
		account_currency = frappe.db.get_value('Account', account_name, 'account_currency')
		if chosen_currency == account_currency:
			banks.append(ba['name'])
	return banks

	

@frappe.whitelist()
def get_receivable_account_by_currency(chosen_currency = None):
	receivables = []
	accounts = frappe.db.get_all('Account', {'account_type' : 'receivable', 'account_currency': chosen_currency}, 'name')
	for a in accounts:
		receivables.append(a['name'])
	return receivables
