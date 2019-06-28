# -*- coding: utf-8 -*-
# Copyright (c) 2015, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe import utils
from frappe.model.document import Document
import datetime
from datetime import datetime
import json
from erpnext.accounts.utils import get_fiscal_year
from shei.shei.report.accounts_receivable_shei.accounts_receivable_shei import ReceivablePayableReport
from shei.shei.report.accounts_receivable_us_shei.accounts_receivable_us_shei import ReceivablePayableReport as ReceivablePayableReportUS


class CompanyStats(Document):

    def onload(self):
        self.exchange_rate = self.get_rate_exchange_us_cad()
        self.btn_load_resume_button()        

    def btn_load_resume_button(self):
        self.clear_tables()
        self.set_sales_order_report()
        self.set_receivable_report()
        self.set_payable_report()
        self.set_quote_report()
        self.set_sales_invoice_report()
        self.set_deposit_report()

    def clear_tables(self):
        self.set("sales_order_today_table", [])
        self.set("sales_order_curr_month", [])
        self.set("si_table_today", [])
        self.set("si_table_month", [])
        self.set("quote_table_today", [])
        self.set("quote_table_month", [])
        self.set("quote_table_one_year_old", [])

    def load_complete_report(self):
        '''Display rows in the tables with details instead of grouping them by sales person'''
        self.clear_tables()
        sales_orders = self.get_all_sales_order_for_today()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("sales_order_today_table", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount, 'customer_type': 'Customer', 'customer': so.customer})
        sales_orders = self.get_all_sales_order_for_curr_month()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("sales_order_curr_month", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount, 'customer_type': 'Customer', 'customer': so.customer})
        sales_invoices = self.get_all_sales_invoice_for_today()
        for si in sales_invoices:
            si_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Invoice', 'parent': si.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("si_table_today", {'doctype_type': 'Sales Invoice', 'doctype_id': si.name, 'sales_person': si_sales_person.sales_person, 'amount': si_sales_person.allocated_amount, 'customer_type': 'Customer', 'customer': si.customer})
        sales_invoices = self.get_all_sales_invoice_for_curr_month()
        for si in sales_invoices:
            si_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Invoice', 'parent': si.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("si_table_month", {'doctype_type': 'Sales Invoice', 'doctype_id': si.name, 'sales_person': si_sales_person.sales_person, 'amount': si_sales_person.allocated_amount, 'customer_type': 'Customer', 'customer': si.customer})
        quotations = self.get_all_quote_for_today()
        for quote in quotations:
            self.append("quote_table_today", {'doctype_type': 'Quotation', 'doctype_id': quote.name, 'customer_type': quote.quotation_to, 'customer': quote.customer or quote.lead, 'sales_person': quote.sales_person, 'amount': quote.base_total})
        quotations = self.get_all_quote_for_curr_month()
        for quote in quotations:
            self.append("quote_table_month", {'doctype_type': 'Quotation', 'doctype_id': quote.name, 'customer_type': quote.quotation_to, 'customer': quote.customer or quote.lead, 'sales_person': quote.sales_person, 'amount': quote.base_total})
        quotations = self.get_all_quote_open_since_past_year()
        for quote in quotations:
            self.append("quote_table_one_year_old", {'doctype_type': 'Quotation', 'doctype_id': quote.name, 'customer_type': quote.quotation_to, 'customer': quote.customer or quote.lead, 'sales_person': quote.sales_person, 'amount': quote.base_total})

    def get_curr_day(self):
        return datetime.strptime(utils.today(), '%Y-%m-%d')

    def get_start_of_year(self):
        '''get start of current fiscal year'''
        start_year = get_fiscal_year(date=self.get_curr_day(), company=frappe.db.get_default("company"), as_dict=True)
        return start_year['year_start_date']

    def get_all_sales_team_as_dict(self):
        sales_team_dict = {}
        sales_team_list = frappe.db.get_all('Sales Person', fields={'name'})
        for st in sales_team_list:
            sales_team_dict[st.name] = 0
        return sales_team_dict

    def get_all_sales_order_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Sales Order', filters={'transaction_date': now, 'status': ('NOT IN', "Draft, Cancelled")}, fields={'base_total', 'name', 'customer'})

    def get_all_sales_order_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('between', (mtd, now)), 'status': ('NOT IN', "Draft, Cancelled")}, fields={'base_total', 'name', 'customer'})

    def get_all_sales_order_for_curr_year(self):
        now = self.get_curr_day()
        ytd = self.get_start_of_year()
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('between', (ytd, now)), 'status': ('NOT IN', "Draft, Cancelled")}, fields={'base_total', 'name', 'customer'})

    def get_all_open_sales_order_for_curr_year(self):
        #now = self.get_curr_day()
        #ytd = self.get_start_of_year()
        return frappe.db.get_all('Sales Order', filters={'status': ('NOT IN', 'Draft, Cancelled, Closed, Completed')}, fields={'base_total', 'name', 'customer'})

    def group_so_by_sales_person(self, sales_orders=[]):
        '''Returns a dict of sales person and the total amount of sales order they make'''
        sales_team_dict = self.get_all_sales_team_as_dict()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})
            for sp in so_sales_person:
                sales_team_dict[sp.sales_person] = sales_team_dict[sp.sales_person] + so.base_total
        return sales_team_dict        
        
    def get_all_sales_invoice_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Sales Invoice', filters={'posting_date': now, 'status': ('NOT IN', "Draft, Cancelled"), 'customer': ("NOT IN", "THE SH GROUP, SYSTEME HUNTINGDON INC.")}, fields={'base_total', 'name', 'customer'})

    def get_all_sales_invoice_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        now = datetime.date(now)
        mtd = datetime.date(mtd)
        return frappe.db.get_all('Sales Invoice', filters={'posting_date': ('between', (mtd, now)), 'status': ('NOT IN', "Draft, Cancelled"), 'customer': ("NOT IN", "THE SH GROUP, SYSTEME HUNTINGDON INC.")}, fields={'base_total', 'name', 'customer'})

    def get_all_sales_invoice_for_curr_year(self):
        now = self.get_curr_day()
        ytd = self.get_start_of_year()
        return frappe.db.get_all('Sales Invoice', filters={'posting_date': ('between', (ytd, now)), 'status': ('NOT IN', "Draft, Cancelled"), 'customer': ("NOT IN", "THE SH GROUP, SYSTEME HUNTINGDON INC.")}, fields={'base_total', 'name', 'customer'})

    def group_si_by_sales_person(self, sales_invoices=[]):
        '''Returns a dict of sales person and the total amount of sales invoice they make'''
        sales_team_dict = self.get_all_sales_team_as_dict()
        for si in sales_invoices:
            si_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Invoice', 'parent': si.name}, {'allocated_amount', 'sales_person'})
            for sp in si_sales_person:
                sales_team_dict[sp.sales_person] = sales_team_dict[sp.sales_person] + si.base_total
        return sales_team_dict        

    def set_sales_invoice_today(self):
        sales_invoices = self.get_all_sales_invoice_for_today()
        sales_team_dict = self.group_si_by_sales_person(sales_invoices)
        self.si_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("si_table_today", {'sales_person': key, 'amount': value})

    def set_sales_invoice_curr_month(self):
        sales_invoices = self.get_all_sales_invoice_for_curr_month()
        sales_team_dict = self.group_si_by_sales_person(sales_invoices)
        self.si_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("si_table_month", {'sales_person': key, 'amount': value})

    def set_sales_invoice_curr_year(self):
        sales_invoices = self.get_all_sales_invoice_for_curr_year()
        sales_team_dict = self.group_si_by_sales_person(sales_invoices)
        self.si_curr_year = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("si_table_year", {'sales_person': key, 'amount': value})

    def set_sales_invoice_report(self):
        self.set_sales_invoice_today()
        self.set_sales_invoice_curr_month()
        self.set_sales_invoice_curr_year()
        
    def set_sales_order_today(self):
        sales_orders = self.get_all_sales_order_for_today()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("sales_order_today_table", {'sales_person': key, 'amount': value})

    def set_sales_order_curr_month(self):
        sales_orders = self.get_all_sales_order_for_curr_month()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("sales_order_curr_month", {'sales_person': key, 'amount': value})

    def set_sales_order_curr_year(self):
        sales_orders = self.get_all_sales_order_for_curr_year()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_curr_year = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("sales_order_curr_year", {'sales_person': key, 'amount': value})

    def set_open_sales_order(self):
        sales_orders = self.get_all_open_sales_order_for_curr_year()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.oo_curr_open = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("oo_table_curr_open_order", {'sales_person': key, 'amount': value})

    def set_sales_order_report(self):
        self.set_sales_order_today()
        self.set_sales_order_curr_month()
        self.set_sales_order_curr_year()
        self.set_open_sales_order()
        
    def get_all_quote_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': now, 'status': ('NOT IN', 'Draft, Lost, Cancelled'), 'other_version_existing_quote_sh_':False}, fields={'base_total', 'name', 'sales_person', 'quotation_to', 'customer', 'lead'}) #if quote is from lead, there's no customer, just a customer_namr

    def get_all_quote_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': ('between', (mtd, now)), 'status': ('NOT IN', 'Draft, Cancelled'), 'other_version_existing_quote_sh_':False}, fields={'base_total', 'name', 'sales_person', 'quotation_to', 'customer', 'lead'})

    def get_all_quote_for_curr_year(self):
        now = self.get_curr_day()
        ytd = self.get_start_of_year()
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': ('between', (ytd, now)), 'status': ('NOT IN', 'Draft, Cancelled'), 'other_version_existing_quote_sh_':False}, fields={'base_total', 'name', 'sales_person', 'quotation_to', 'customer', 'lead'})

    def get_all_quote_open_since_past_year(self):
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'status': ('NOT IN', 'Draft, Ordered, Lost, Cancelled'), 'other_version_existing_quote_sh_':False}, fields={'base_total', 'name', 'sales_person', 'quotation_to', 'customer', 'lead'})

    def group_quote_by_sales_person(self, quotes=[]):
        sales_team_dict = self.get_all_sales_team_as_dict()
        have_other = False
        for quote in quotes:
            if quote.sales_person:
    			sales_team_dict[quote.sales_person] = sales_team_dict[quote.sales_person] + quote.base_total
            elif not have_other: #if no sales person for the quote, we want to create a new key in dict: 'Other'
                sales_team_dict["Other"] = quote.base_total
                have_other = True
            else:
                sales_team_dict["Other"] = sales_team_dict["Other"] + quote.base_total
        return sales_team_dict

    def set_quote_today(self):
        quotes = self.get_all_quote_for_today()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_today", {'sales_person': key, 'amount': value})

    def set_quote_curr_month(self):
        quotes = self.get_all_quote_for_curr_month()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_month", {'sales_person': key, 'amount': value})

    def set_quote_curr_year(self):
        quotes = self.get_all_quote_for_curr_year()        
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_curr_year = sum(sales_team_dict.values())

    def set_quote_older_than_a_year(self):
        quotes = self.get_all_quote_open_since_past_year()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_one_year_open = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_one_year_old", {'sales_person': key, 'amount': value})

    def set_quote_report(self):
	    self.set_quote_today()
	    self.set_quote_curr_month()
	    self.set_quote_curr_year()
	    self.set_quote_older_than_a_year()

    def get_rate_exchange_us_cad(self):
        rate = frappe.db.get_values('Currency Exchange', {'from_currency':'USD', 'to_currency':'CAD'}, ['exchange_rate'], order_by='creation', as_dict=True)[-1]['exchange_rate']
        return rate

    def set_receivable_cd_cad(self, args={}):
        filters = {'advance_payment': 'Only CD-', 'currency': 'CAD', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_cad = ReceivablePayableReport(filters)
        data = self.get_report_data(receivable_cad, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_cad = outstanding

    def set_receivable_without_cd_cad(self, args={}):
        filters = {'advance_payment': 'Remove CD-', 'currency': 'CAD', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_cad_without_cd = ReceivablePayableReport(filters)
        data = self.get_report_data(receivable_cad_without_cd, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_cad_without_cd = outstanding
        ageing_curr_to_thirty_cad = sum([row['0_30'] for row in data])
        self.ageing_curr_to_thirty_cad = ageing_curr_to_thirty_cad
        ageing_thirdy_to_sixty_cad = sum([row['31_60'] for row in data])
        self.ageing_thirdy_to_sixty_cad = ageing_thirdy_to_sixty_cad
        ageing_sixty_to_ninety_cad = sum([row['61_90'] for row in data])
        ageing_ninety_and_more_cad = sum([row['91_above'] for row in data])
        self.ageing_sixty_and_more_cad = ageing_sixty_to_ninety_cad + ageing_ninety_and_more_cad

    def set_receivable_cd_usd(self, args={}):
        filters = {'advance_payment': 'Only CD-', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_usd = ReceivablePayableReportUS(filters)
        data = self.get_report_data(receivable_usd, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_usd = outstanding * self.exchange_rate

    def set_receivable_without_cd_usd(self, args={}):
        filters = {'advance_payment': 'Remove CD-', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_usd_without_cd = ReceivablePayableReportUS(filters)
        data = self.get_report_data(receivable_usd_without_cd, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_usd_without_cd = outstanding * self.exchange_rate
        ageing_curr_to_thirty_usd = sum([row['0_30'] for row in data])
        self.ageing_curr_to_thirty_usd = ageing_curr_to_thirty_usd * self.exchange_rate
        ageing_thirdy_to_sixty_usd = sum([row['31_60'] for row in data])
        self.ageing_thirdy_to_sixty_usd = ageing_thirdy_to_sixty_usd * self.exchange_rate
        ageing_sixty_and_more_usd = sum([row['61_90'] for row in data])
        ageing_ninety_and_more_usd = sum([row['91_above'] for row in data])
        self.ageing_sixty_and_more_usd = (ageing_sixty_and_more_usd + ageing_ninety_and_more_usd) * self.exchange_rate

    def get_report_data(self, obj, args={}):
        result = obj.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        return data

    def set_receivable_report(self):
        args = {   
            "party_type": "Customer",
            "naming_by": ["Selling Settings", "cust_master_name"],
        }
        self.set_receivable_cd_cad(args)
        self.set_receivable_without_cd_cad(args)
        self.set_receivable_cd_usd(args)
        self.set_receivable_without_cd_usd(args)

    def set_payable_cad(self, args={}):
        filters = {'company': frappe.defaults.get_user_default("Company"), 'currency': frappe.defaults.get_user_default("currency"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        payable_cad = ReceivablePayableReport(filters)
        data = self.get_report_data(payable_cad, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.payable_cad = outstanding

    def set_payable_usd(self, args={}):
        filters = {'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        payable_usd = ReceivablePayableReportUS(filters)
        data = self.get_report_data(payable_usd, args)
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.payable_usd = outstanding * self.exchange_rate

    def set_payable_report(self):
        args = {
            "party_type": "Supplier",
            "naming_by": ["Buying Settings", "supp_master_name"]
	    }
        self.set_payable_cad(args)
        self.set_payable_usd(args)

    def get_all_payment_entry_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Payment Entry', filters={'payment_type': 'Receive', 'docstatus':1, 'posting_date': now}, fields={'base_paid_amount', 'name'})

    def get_all_payment_entry_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Payment Entry', filters={'payment_type': 'Receive', 'docstatus':1, 'posting_date': ('between', (mtd, now))}, fields={'base_paid_amount', 'name'})

    def get_all_customer_deposit_for_today(self):
        now = self.get_curr_day()
        customer_deposits = frappe.db.get_all('Customer Deposit', filters={'posting_date': now}, fields={'name'})
        amount = 0
        for cd in customer_deposits:
            deposits = frappe.db.get_all('Customer Deposit Quotation', filters={'parenttype': 'Customer Deposit', 'parent': cd.name}, fields={'grand_total'})
            amount = amount + sum(d.grand_total for d in deposits)
        return amount

    def get_all_customer_deposit_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        customer_deposits = frappe.db.get_all('Customer Deposit', filters={'posting_date': ('between', (mtd, now))}, fields={'name'})
        amount = 0
        for cd in customer_deposits:
            deposits = frappe.db.get_all('Customer Deposit Quotation', filters={'parenttype': 'Customer Deposit', 'parent': cd.name}, fields={'grand_total'})
            amount = amount + sum(d.grand_total for d in deposits)
        return amount

    def set_deposit_report(self):
        #get all payment entry made today
        payment_entries = self.get_all_payment_entry_for_today()
        self.pe_today = sum(pe.base_paid_amount for pe in payment_entries)

        #get all payment entry made this month
        payment_entries = self.get_all_payment_entry_for_curr_month()
        self.pe_curr_month = sum(pe.base_paid_amount for pe in payment_entries)

        #set customer deposit made today & month
        self.cd_today = self.get_all_customer_deposit_for_today()
        self.cd_curr_month = self.get_all_customer_deposit_for_curr_month()
