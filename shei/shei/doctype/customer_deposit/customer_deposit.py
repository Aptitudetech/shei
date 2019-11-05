# -*- coding: utf-8 -*-
# Copyright (c) 2017, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate
from erpnext.accounts.doctype.journal_entry.journal_entry import get_exchange_rate

class CustomerDeposit(Document):

        def update_posting_date(self):
                count = 0
                for i in frappe.get_list("Customer Deposit", fields=["name", "customer_deposit_application", "final_invoice_date"], filters={"docstatus": 1}):
			if i.final_invoice_date:
				frappe.db.set_value("Journal Entry", i.customer_deposit_application, "posting_date", i.final_invoice_date)
                        	count = count + 1
                frappe.msgprint(str(count) + " JV were updated")

        def on_cancel(self):
                if self.customer_deposit_reception:
                        je = frappe.get_doc("Journal Entry", self.customer_deposit_reception)
                        je.cancel()
                        je.delete()
                        frappe.db.set_value("Customer Deposit", self.name, "customer_deposit_reception", "")
                if self.customer_deposit_application:
                        je = frappe.get_doc("Journal Entry", self.customer_deposit_application)
                        je.cancel()
                        je.delete()
                        frappe.db.set_value("Customer Deposit", self.name, "customer_deposit_application", "")
                for i in self.get('customer_deposit_quotation'):
                        frappe.db.set_value("Quotation", i.quotation, "customer_deposit_received", False)
			set_project_customer_deposit("cancel", self.project, i.quotation)

        def get_customer_deposit_quotation(self):
                self.customer_deposit_quotation = []
                for qt in frappe.get_list("Quotation", fields=["name", "total", "grand_total", "status"], filters={"customer_deposit": True, "customer_deposit_received": False, "docstatus": 1, "party_name": self.customer}):
                        self.append("customer_deposit_quotation", {
                                "quotation": qt.name,
                                "total_before_taxes": qt.total,
                                "grand_total": qt.grand_total
                        })
 
        def apply_customer_deposit(self):
                if not self.customer_deposit_application:
                        customer_currency = frappe.db.get_value("Customer", {'name':self.customer}, "default_currency")
                        if not customer_currency:
                                customer_currency = 'CAD'
                        accounts = frappe.get_all('Party Account', fields=['*'], filters={'parenttype': 'Customer', 'parent': self.customer})
                        if accounts:
                                #take the account from the table
                                rec_account = accounts[0]['account']
                        else: 
                                #take default receivable account
                                rec_account = frappe.db.get_value('Company', {'name':frappe.db.get_default("company")}, 'default_receivable_account')


                        deposit_account = frappe.db.get_value('Bank Account', { 'currency': customer_currency, 'is_deposit_account': True}, 'deposit_account')
                        if customer_currency == "USD":
                                multi_currency = True
                        #        rec_account = "12150 COMPTES CLIENTS US (ERP) - SHI"
                        #        deposit_account = "21450 AVANCES CLIENTS US - SHI"
                        elif customer_currency == "CAD" or customer_currency is None:
                                multi_currency = False
                        #        rec_account = "12100 COMPTES CLIENTS (ERP) - SHI"
                        #        deposit_account = "21400 AVANCES CLIENT CDN - SHI"
                        else:
                                frappe.msgprint("The currency of customer " + self.customer + " is not supported by this module at this time.", raise_exception=True)
                        je = frappe.new_doc("Journal Entry")
                        json_update = {
                                "naming_series": "CD-",
                                "voucher_type": "Journal Entry",
                                "posting_date": self.final_invoice_date,
                                "company": frappe.db.get_default("company"),
                                "multi_currency" : multi_currency,
                                "remark": "Application of Customer Deposit against normal receivable account",
                                "write_off_based_on": "Accounts Receivable",
                                "write_off_amount": 0,
                                "pay_to_recd_from": self.customer,
                                "letter_head" : "Standard - header & footer",
                                "is_opening": "No",
                        }
                        je.update (json_update)

                        #On passe toutes les soumissions pour renverser les taxes (si <> USD) et appliquer les totaux envers le compte Recevable par défaut
                        ref = ""
                        for i in self.get('customer_deposit_quotation'):
                                qt = frappe.get_doc("Quotation", i.quotation)
				set_project_customer_deposit("apply", self.project, i.quotation)
                                if ref:
                                        ref = ref + ", " + qt.name
                                else:
                                        ref = qt.name

                                dep_ex_rate = get_exchange_rate(self.posting_date, deposit_account)

				if self.final_invoice_date:
					cur_ex_rate = get_exchange_rate(self.final_invoice_date, rec_account)
				else:
					exit()
                                base_cr = qt.grand_total * cur_ex_rate
                                base_dt = qt.grand_total * dep_ex_rate

                                je.append("accounts", {
                                        "account": deposit_account,
                                        "balance": 0,
                                        "cost_center": "Main - SHI",
                                        "party_type": "Customer",
                                        "party": self.customer,
                                        "party_balance": 0,
                                        "exchange_rate": dep_ex_rate,
                                        "debit_in_account_currency": round(qt.grand_total, 2),
                                        "debit": round(base_dt, 2),
                                        "credit_in_account_currency": 0,
                                        "credit": 0,
                                        "project": self.project,
                                        "is_advance": "No"
                                })
                                je.append("accounts", {
                                        "account": rec_account,
                                        "balance": 0,
                                        "cost_center": "Main - SHI",
                                        "party_type": "Customer",
                                        "party": self.customer,
                                        "exchange_rate": cur_ex_rate,
                                        "debit_in_account_currency": 0,
                                        "debit": 0,
                                        "credit_in_account_currency": round(qt.grand_total, 2),
                                        "credit": round(base_cr, 2),
                                        "project": self.project,
                                        "is_advance": "Yes"
                                })
                                if multi_currency:
                                        total_d = 0.00
                                        total_c = 0.00
                                        total_diff = 0.00
                                        for i in je.get('accounts'):
                                                if i.debit != 0.00:
                                                        total_d = total_d + i.debit
                                                if i.credit != 0.00:
                                                        total_c = total_c + i.credit
                                        total_diff = total_d - total_c
                                        if total_diff < 0.00:
                                                field = "debit_in_account_currency"
                                                total_diff = abs(total_diff)
                                        else:
                                                field = "credit_in_account_currency"

					if total_diff <> 0.0000:	
						je.append("accounts", {
							"account": "48900 GAIN PERTE - DEVISE US - SHI",
							"exchange_rate": 1,
							field: round(total_diff, 2),
							"project": self.project,
						})

                                # On débite les taxes dans les comptes de taxes et on crédite le compte de taxes temporaire
                                for t in qt.get('taxes'):
                                        je.append("accounts", {
                                                "account": t.account_head,
                                                "balance": 0,
                                                "cost_center": "Main - SHI",
                                                "debit_in_account_currency" : t.tax_amount,
                                                "debit": t.base_tax_amount,
                                                "credit_in_account_currency" : 0,
                                                "credit" : 0,
                                                "project" : self.project,
                                        })
                                        je.append("accounts", {
                                                "account": "21401 - Avance Client CN Sales Tax - SHI",
                                                "balance": 0,
                                                "cost_center": "Main - SHI",
                                                "debit_in_account_currency" : 0,
                                                "debit": 0,
                                                "credit_in_account_currency" : t.tax_amount,
                                                "credit" : t.base_tax_amount,
                                                "project" : self.project,
                                        })
                        json_update = {
                                "user_remark": "Applying customer deposit (Ref.: " + ref + ") to default receivable account",
                        }
                        je.update (json_update)
                        je.save()
                        frappe.db.set_value("Customer Deposit", self.name, "customer_deposit_application", je.name)
			for i in je.get('accounts'):
				if i.account == deposit_account:
					i.reference_type = "Journal Entry"
					i.reference_name = self.customer_deposit_reception
                        je.submit()
			frappe.msgprint("Customer Deposit applied successfully")
                else:
                        frappe.msgprint("This Customer Deposit has already been applied")

        def on_submit(self):
                customer_currency = frappe.db.get_value("Customer", {'name': self.customer}, "default_currency")
                if not customer_currency:
                        customer_currency = 'CAD'
                bank_account = frappe.db.get_value('Bank Account', { 'currency': customer_currency, 'is_deposit_account': True}, 'account')
                deposit_account = frappe.db.get_value('Bank Account', { 'currency': customer_currency, 'is_deposit_account': True}, 'deposit_account')
                
                if customer_currency == "USD":
                        multi_currency = True
                #        bank_account = "11118 BANQUE DE MONTRÉAL (US) (4600-419) - SHI"
                #        deposit_account = "21450 AVANCES CLIENTS US - SHI"
                elif customer_currency == "CAD":
                        multi_currency = False
                #        bank_account = "11114 BANQUE DE MONTREAL (1011-290) - SHI"
                #        deposit_account = "21400 AVANCES CLIENT CDN - SHI"
                else:
                        frappe.msgprint("The currency of customer " + self.customer + " is not supported by this module at this time.", raise_exception=True)

                je = frappe.new_doc("Journal Entry")
                json_update = {
                        "naming_series": "CD-",
                        "voucher_type": "Cash Entry",
                        "posting_date": self.posting_date,
                        "company": frappe.db.get_default("company"),
                        "multi_currency" : multi_currency,
                        "remark": "Deposit",
                        "write_off_based_on": "Accounts Receivable",
                        "write_off_amount": 0,
                        "pay_to_recd_from": self.customer,
                        "letter_head" : "Standard - header & footer",
                        "is_opening": "No",
			"cheque_no": self.reference_no,
			"cheque_date": self.reference_date,
                }
                je.update (json_update)

                #On passe toutes les soumissions pour appliquer les taxes (si <> USD) et totaux envers le compte Avances Client
                ref = ""
                for i in self.get('customer_deposit_quotation'):
                        qt = frappe.get_doc("Quotation", i.quotation)
			set_project_customer_deposit("submit", self.project, i.quotation, self.posting_date, self.name)
                        frappe.db.set_value("Quotation", i.quotation, "customer_deposit_received", True)
                        if ref:
                                ref = ref + ", " + qt.name
                        else:
                                ref = qt.name

                        je.append("accounts", {
                                "account": deposit_account,
                                "balance": 0,
                                "cost_center": "Main - SHI",
                                "party_type": "Customer",
                                "party": self.customer,
                                "party_balance": 0,
                                "account_currency": qt.currency,
                                "debit_in_account_currency" : 0,
                                "debit": 0,
                                "credit_in_account_currency" : qt.grand_total,
                                "credit" : qt.base_grand_total,
                                "project" : self.project,
                                "is_advance" : "Yes"
                        })
                        je.append("accounts", {
                                "account": bank_account,
                                "balance": 0,
                                "cost_center": "Main - SHI",
                                "account_currency": qt.currency,
                                "debit_in_account_currency" : qt.grand_total,
                                "debit": qt.base_grand_total,
                                "credit_in_account_currency" : 0,
                                "credit" : 0,
                                "project" : self.project,
                        })

                        # On crédite les taxes dans les comptes de taxes et on débite dans le compte de taxes temporaire
                        for t in qt.get('taxes'):
                                je.append("accounts", {
                                        "account": t.account_head,
                                        "balance": 0,
                                        "cost_center": "Main - SHI",
                                        "account_currency": qt.currency,
                                        "debit_in_account_currency" : 0,
                                        "debit": 0,
                                        "credit_in_account_currency" : t.tax_amount,
                                        "credit" : t.base_tax_amount,
                                        "project" : self.project,
                                        "is_advance" : "No"
                                })
                                je.append("accounts", {
                                        "account": "21401 - Avance Client CN Sales Tax - SHI",
                                        "balance": 0,
                                        "cost_center": "Main - SHI",
                                        "account_currency": qt.currency,
                                        "debit_in_account_currency" : t.tax_amount,
                                        "debit": t.base_tax_amount,
                                        "credit_in_account_currency" : 0,
                                        "credit" : 0,
                                        "project" : self.project,
                                        "is_advance" : "No"
                                })
                json_update = {
                        "user_remark": "Applying customer deposit (Ref.: " + ref + ") to Avance Client receivable account",
                }
                je.update (json_update)
                je.save()
                frappe.db.set_value("Customer Deposit", self.name, "customer_deposit_reception", je.name)
                je.submit()

def set_project_customer_deposit(action, project_name, pfi, reception_date=None, customer_deposit=None):

        pj = frappe.get_doc("Project", project_name)
        for i in pj.get('customer_deposit_item'):
                if i.deposit_invoice == pfi:
                        if action == "submit":
                                i.reception_date = reception_date
                                i.customer_deposit = customer_deposit
                        elif action == "apply":
                                i.deposit_applied = True
                        elif action == "cancel":
                                i.deposit_applied = False
				i.customer_deposit = ""
        pj.save()
