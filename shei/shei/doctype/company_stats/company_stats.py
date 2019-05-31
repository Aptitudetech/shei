# -*- coding: utf-8 -*-
# Copyright (c) 2015, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import datetime
from datetime import datetime
from shei.shei.report.accounts_receivable_shei.accounts_receivable_shei import ReceivablePayableReport
from shei.shei.report.accounts_receivable_us_shei.accounts_receivable_us_shei import ReceivablePayableReport as ReceivablePayableReportUS
import json 
#from shei.shei.report.accounts_receivable_shei.accounts_receivable_shei import __init__

class CompanyStats(Document):

    def onload(self):
        self.btn_load_resume_button()        

    def btn_load_resume_button(self):
        self.clear_tables()
        self.set_sales_order_report()
        self.set_receivable_report()
        self.set_payable_report()
        self.set_quote_report()
        self.set_deposit_report()

    def clear_tables(self):
        self.set("sales_order_today_table", [])
        self.set("sales_order_curr_month", [])
        self.set("oo_table_today", [])
        self.set("oo_table_curr_month", [])
        self.set("quote_table_today", [])
        self.set("quote_table_month", [])
        self.set("quote_table_one_year_old", [])

    def load_complete_report(self):
        self.clear_tables()
        sales_orders = self.get_all_sales_order_for_today()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("sales_order_today_table", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount})
        sales_orders = self.get_all_sales_order_for_curr_month()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("sales_order_curr_month", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount})
        sales_orders = self.get_all_open_sales_order_for_today()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("oo_table_today", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount})
        sales_orders = self.get_all_open_sales_order_for_curr_month()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})[0]            
            self.append("oo_table_curr_month", {'doctype_type': 'Sales Order', 'doctype_id': so.name, 'sales_person': so_sales_person.sales_person, 'amount': so_sales_person.allocated_amount})
        quotations = self.get_all_quote_for_today()
        for quote in quotations:
            self.append("quote_table_today", {'doctype_type': 'Sales Order', 'doctype_id': quote.name, 'sales_person': quote.sales_person, 'amount': quote.base_grand_total})
        quotations = self.get_all_quote_for_curr_month()
        for quote in quotations:
            self.append("quote_table_month", {'doctype_type': 'Sales Order', 'doctype_id': quote.name, 'sales_person': quote.sales_person, 'amount': quote.base_grand_total})
        quotations = self.get_all_quote_open_since_past_year()
        for quote in quotations:
            self.append("quote_table_one_year_old", {'doctype_type': 'Sales Order', 'doctype_id': quote.name, 'sales_person': quote.sales_person, 'amount': quote.base_grand_total})

    def get_curr_day(self):
        return datetime.now()

    def get_all_sales_team_as_dict(self):
        sales_team_dict = {}
        sales_team_list = frappe.db.get_all('Sales Person', fields={'name'})
        for st in sales_team_list:
            sales_team_dict[st.name] = 0
        sales_team_dict['Other'] = 0 #Some Sales Order don't have a sales Person
        return sales_team_dict

    def get_all_sales_order_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Sales Order', filters={'transaction_date': now}, fields={'base_grand_total', 'name'})

    def get_all_sales_order_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('<=', now) and ('>=', mtd)}, fields={'base_grand_total', 'name'})

    def get_all_sales_order_for_curr_year(self):
        now = self.get_curr_day()
        ytd = now.replace(year = now.year-1, month=11, day=1)
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('<=', now) and ('>=', ytd)}, fields={'base_grand_total', 'name'})

    def get_all_open_sales_order_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Sales Order', filters={'transaction_date': now, 'status': ('IN', 'To Bill, To Deliver and Bill')}, fields={'base_grand_total', 'name'})

    def get_all_open_sales_order_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('<=', now) and ('>=', mtd), 'status': ('IN', 'To Bill, To Deliver and Bill')}, fields={'base_grand_total', 'name'})

    def get_all_open_sales_order_for_curr_year(self):
        now = self.get_curr_day()
        ytd = now.replace(year = now.year-1, month=11, day=1)
        return frappe.db.get_all('Sales Order', filters={'transaction_date': ('<=', now) and ('>=', ytd), 'status': ('IN', 'To Bill, To Deliver and Bill')}, fields={'base_grand_total', 'name'})

    def group_so_by_sales_person(self, sales_orders=[]):
        sales_team_dict = self.get_all_sales_team_as_dict()
        for so in sales_orders:
            so_sales_person = frappe.db.get_all('Sales Team', {'parenttype': 'Sales Order', 'parent': so.name}, {'allocated_amount', 'sales_person'})
            for sp in so_sales_person:
                sales_team_dict[sp.sales_person] = sales_team_dict[sp.sales_person] + so.base_grand_total
            if not so_sales_person:
                sales_team_dict['Other'] = sales_team_dict['Other'] + so.base_grand_total
        return sales_team_dict        

    def set_sales_order_report(self):
        #get/group all sales order made today
        sales_orders = self.get_all_sales_order_for_today()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("sales_order_today_table", {'sales_person': key, 'amount': value})

        #get/group all sales order made this month
        sales_orders = self.get_all_sales_order_for_curr_month()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("sales_order_curr_month", {'sales_person': key, 'amount': value})

        #get/group all sales order made this year
        sales_orders = self.get_all_sales_order_for_curr_year()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.so_curr_year = sum(sales_team_dict.values())

        #get/group all open order made this today
        sales_orders = self.get_all_open_sales_order_for_today()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.oo_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("oo_table_today", {'sales_person': key, 'amount': value})

        #get/group all sales order made this month
        sales_orders = self.get_all_open_sales_order_for_curr_month()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.oo_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("oo_table_curr_month", {'sales_person': key, 'amount': value})

        #get/group all sales order made this year
        sales_orders = self.get_all_open_sales_order_for_curr_year()
        sales_team_dict = self.group_so_by_sales_person(sales_orders)
        self.oo_curr_year = sum(sales_team_dict.values())

    
    def get_all_quote_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': now, 'status': 'Submitted',}, fields={'base_grand_total', 'name', 'sales_person'})

    def get_all_quote_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': ('<=', now) and ('>=', mtd), 'status': 'Submitted'}, fields={'base_grand_total', 'name', 'sales_person'})

    def get_all_quote_for_curr_year(self):
        now = self.get_curr_day()
        ytd = now.replace(year = now.year-1, month=11, day=1)
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': ('<=', now) and ('>=', ytd), 'status': 'Submitted'}, fields={'base_grand_total', 'name', 'sales_person'})

    def get_all_quote_open_since_past_year(self):
        now = self.get_curr_day()
        ytd = now.replace(year = now.year-1)
        return frappe.db.get_all('Quotation', filters={'name': ('like', '%QTN%'), 'transaction_date': ('<=', ytd), 'status': 'Draft'}, fields={'base_grand_total', 'name', 'sales_person'})

    def group_quote_by_sales_person(self, quotes=[]):
        sales_team_dict = self.get_all_sales_team_as_dict()
        for quote in quotes:
            if quote.sales_person:
    			sales_team_dict[quote.sales_person] = sales_team_dict[quote.sales_person] + quote.base_grand_total
            else:
                sales_team_dict['Other'] = sales_team_dict['Other'] + quote.base_grand_total
        return sales_team_dict

    def set_quote_report(self):
	    #get/group all Quotes made today
        quotes = self.get_all_quote_for_today()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_today = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_today", {'sales_person': key, 'amount': value})

        #get/group all Quotes made this month
        quotes = self.get_all_quote_for_curr_month()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_curr_month = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_month", {'sales_person': key, 'amount': value})

        #get/group all Quotes made this year
        quotes = self.get_all_quote_for_curr_year()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_curr_year = sum(sales_team_dict.values())

        #get/group all Quotes older than a year
        quotes = self.get_all_quote_open_since_past_year()
        sales_team_dict = self.group_quote_by_sales_person(quotes)
        self.quote_one_year_open = sum(sales_team_dict.values())
        for key,value in sales_team_dict.iteritems():
            self.append("quote_table_one_year_old", {'sales_person': key, 'amount': value})


    def set_receivable_report(self):
        args = {   
            "party_type": "Customer",
            "naming_by": ["Selling Settings", "cust_master_name"],
        }
        filters = {'advance_payment': 'Only CD-', 'currency': 'CAD', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_cad = ReceivablePayableReport(filters)
        result = receivable_cad.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_cad = outstanding

        #get receivable account CAD Without Customer Deposit
        filters = {'advance_payment': 'Remove CD-', 'currency': 'CAD', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_cad_without_cd = ReceivablePayableReport(filters)
        result = receivable_cad_without_cd.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_cad_without_cd = outstanding
        
        #get receivable account USD With Customer Deposit
        filters = {'advance_payment': 'Only CD-', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_usd = ReceivablePayableReportUS(filters)
        result = receivable_usd.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_usd = outstanding

        #get receivable account USD Without Customer Deposit
        filters = {'advance_payment': 'Remove CD-', 'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        receivable_usd_without_cd = ReceivablePayableReportUS(filters)
        result = receivable_usd_without_cd.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        #frappe.msgprint(_("data: {0}").format(data))

        outstanding = sum([row['outstanding_amount'] for row in data])
        self.receivable_usd_without_cd = outstanding

    def set_payable_report(self):
        args = {
            "party_type": "Supplier",
            "naming_by": ["Buying Settings", "supp_master_name"]
	    }
        #get Payable account cad
        filters = {'company': frappe.defaults.get_user_default("Company"), 'currency': frappe.defaults.get_user_default("currency"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        payable_cad = ReceivablePayableReport(filters)
        result = payable_cad.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.payable_cad = outstanding

        #get Payable account usd
        filters = {'company': frappe.defaults.get_user_default("Company"), 'report_date': datetime.now(), 'ageing_based_on': 'Posting Date', 'range1': '30', 'range2': '60', 'range3': '90'}
        payable_usd = ReceivablePayableReportUS(filters)
        result = payable_usd.run(args)
        columns, data, a, b = result
        columns = map(frappe.scrub, [(r["fieldname"] if isinstance(r, dict) else r.split(':')[0]) for r in columns])
        data = map(dict, [zip(columns, json.loads(frappe.as_json(row))) for row in data if "'Total'" not in row])
        outstanding = sum([row['outstanding_amount'] for row in data])
        self.payable_usd = outstanding

    def get_all_payment_entry_for_today(self):
        now = self.get_curr_day()
        return frappe.db.get_all('Payment Entry', filters={'payment_type': 'Receive', 'posting_date': now}, fields={'base_paid_amount', 'name'})

    def get_all_payment_entry_for_curr_month(self):
        now = self.get_curr_day()
        mtd = now.replace(day=1)
        return frappe.db.get_all('Payment Entry', filters={'payment_type': 'Receive', 'posting_date': ('<=', now) and ('>=', mtd)}, fields={'base_paid_amount', 'name'})

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
        customer_deposits = frappe.db.get_all('Customer Deposit', filters={'posting_date': ('<=', now) and ('>=', mtd)}, fields={'name'})
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

        self.cd_today = self.get_all_customer_deposit_for_today()
        self.cd_curr_month = self.get_all_customer_deposit_for_curr_month()

        self.deposit_today = self.cd_today + self.pe_today
        self.deposit_curr_month = self.cd_curr_month + self.pe_curr_month
