# -*- coding: utf-8 -*-
# Copyright (c) 2015, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document

class AdvancePayment(Document):
	def on_cancel(self):
		a=1
		je = frappe.get_doc("Journal Entry", self.journal_entry)
		je.cancel()
		je.delete()
		frappe.db.set_value("Advance Payment", self.name, "journal_entry", "")
		for i in self.get('items_advances'):
                        frappe.db.set_value("Sales Invoice", i.sales_invoice, "has_been_use_for_advance_payment", False)
			#frappe.msgprint("has been use for")

	def on_submit(self):
		multi_currency = True
		je = frappe.new_doc("Journal Entry")
		json_update = {
                        "naming_series": "JV-",
                        "voucher_type": "Journal Entry",
                        "posting_date": self.posting_date,
                        "company": frappe.db.get_default("company"),
                        "user_remark": "Reversing advance payment to use in invoice",
                        "multi_currency" : 0,
                        "remark": "",
                        "write_off_based_on": "Accounts Receivable",
                        "write_off_amount": 0,
                        "pay_to_recd_from": self.customer,
                        "letter_head" : "Standard - header & footer",
                	"is_opening": "No",
                }
		je.update (json_update)
		
		
		#On passe toutes les factures pour renverser les taxes et montants
		for i in self.get('items_advances'):
			si = frappe.get_doc("Sales Invoice", i.sales_invoice)
			if si.status != "Paid":
				frappe.msgprint("Warning Sales Invoice " + si.name + " has not been paid yet.")
			frappe.db.set_value("Sales Invoice", i.sales_invoice, "has_been_use_for_advance_payment", True)
			if si.conversion_rate == 1:
				multi_currency = False
			for it in si.get('items'):
				je.append("accounts", {
					"account": it.income_account,
	                                "balance": 0,
        	                        "cost_center": "100 Main - SHI",
	                                "account_currency": si.currency,
					"exchange_rate": si.conversion_rate,
					"debit_in_account_currency" : it.base_net_amount,
					"debit": it.net_amount,
					"credit_in_account_currency" : 0,
					"credit" : 0,
					"project" : self.project,
					"is_advance" : "No"
                	        })
			

			je.append("accounts", {
                                "account": frappe.db.get_value("Advance Payment Setup", {'destination_account':si.debit_to}, "origin_account"),
                                "balance": 0,
                                "cost_center": "100 Main - SHI",
                                "party_type": "Customer",
                                "party": self.customer,
                                "party_balance": 0,
                                "account_currency": si.currency,
                                "exchange_rate": si.conversion_rate,
                                "debit_in_account_currency" : 0,
                                "debit": 0,
                                "credit_in_account_currency" : si.grand_total,
                                "credit" : si.base_grand_total,
                                "project" : self.project,
                                "is_advance" : "Yes"
                        })
			
			# On débite les taxes
			for t in si.get('taxes'):
				je.append("accounts", {
	                                "account": t.account_head,
        	                        "balance": 0,
                	                "cost_center": "100 Main - SHI",
        	                        "account_currency": si.currency,
                	                "exchange_rate": si.conversion_rate,
                        	        "debit_in_account_currency" : t.tax_amount,
                                	"debit": t.base_tax_amount,
                        	        "credit_in_account_currency" : 0,
					"credit" : 0,
        	                        "project" : self.project,
                	                "is_advance" : "No"
                        	})
			
			je.multi_currency = multi_currency
			je.save()
		frappe.db.set_value("Advance Payment", self.name, "journal_entry", je.name)
		je.submit()

	def import_advance_payment(self):
		self.items_advances = []
		if self.project:
			for si in frappe.get_list("Sales Invoice", fields=["name", "total", "grand_total", "status"], filters={"is_for_advance_payment": True, "has_been_use_for_advance_payment": False, "docstatus": 1, "project": self.project}):
				if si.status != "Paid":
	                                frappe.msgprint("Warning Sales Invoice " + si.name + " has not been paid yet.")
				
				self.append("items_advances", {
					"sales_invoice": si.name,
					"total_before_taxes": si.total,
					"grand_total": si.grand_total
				})
		else:
			for si in frappe.get_list("Sales Invoice", fields=["name", "total", "grand_total", "status"], filters={"is_for_advance_payment": True, "has_been_use_for_advance_payment": False, "docstatus": 1, "customer": self.customer}):
                                if si.status != "Paid":
	                                frappe.msgprint("Warning Sales Invoice " + si.name + " has not been paid yet.")
				
				self.append("items_advances", {
                                        "sales_invoice": si.name,
                                        "total_before_taxes": si.total,
                                        "grand_total": si.grand_total
                                })
