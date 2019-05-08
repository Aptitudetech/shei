# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import datetime
from datetime import datetime
from itertools import groupby

class CompanyStats(Document):
	
	def onload(self):
		self.set_sales_order_report()
		self.set_receivable_report()
		self.set_payable_report()
		self.set_quote_report()
		self.set_deposit_report()
		frappe.msgprint("Allo234")

	def get_curr_day(self):
		return datetime.now()

	def set_sales_order_report(self):
		now = self.get_curr_day()
		#curr_year = now.year
		sales_person = {}
		mtd = now.replace(day=1)
		#sales_orders = frappe.db.get_all('Sales Order', filters={'creation': ["<=", mtd] and [">=", now]}, fields={'base_grand_total', 'name'})
		sales_orders = frappe.db.get_all('Sales Order', filters={}, fields={'base_grand_total', 'name'})
		sales_orders.sort(key=lambda so: frappe.db.get_value('Sales Team', {'parenttype':'Sales Order', 'parent':so.name}, 'sales_person'))
		frappe.msgprint(_("sales_orders: {0}").format(sales_orders))

		# then use groupby with the same key
		groups = groupby(sales_orders, lambda so: frappe.db.get_value('Sales Team', {'parenttype':'Sales Order', 'parent':so.name}, 'sales_person'))
		frappe.msgprint(_("groups: {0}").format(groups))

		#for adult, group in groups:
	#		print 'adult', adult
	#		for content in group:
#				print '\t', content


		#for so in sales_order:
		#	sales_person = frappe.db.get_all('Sales Team', {'parenttype':'Sales Order', 'parent':so.name}, '*')
		#	for sp in sales_person:
		#		if
		so = sum(s.base_grand_total for s in sales_orders)
		self.so_today = 0.5
		self.so_month_to_date = 0.5
		self.so_year_to_date = 0.5
		self.oo_today = 0.5
		self.oo_month_to_date = 0.5
		self.oo_year_to_date = 0.5

	def set_receivable_report(self):
		self.receivable_cad = 0.5
		self.receivable_cad_without_cd = 0.48
		self.receivable_usd = 0.48
		self.receivable_usd_without_cd = 0.48

	def set_payable_report(self):
		self.payable_cad = 0.48
		self.payable_usd = 0.48

	def set_quote_report(self):
		self.quote_today = 0.48
		self.quote_month_to_date = 0.48
		self.quote_year_to_date = 0.48
		self.list_quotes = []

	def set_deposit_report(self):
		self.pe_today = 0.48
		self.pe_month_to_date = 0.48
		self.cd_today = 0.48
		self.cd_month_to_date = 0.48
		self.deposit_today = 0.48
		self.deposit_month_to_date = 0.48

