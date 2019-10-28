# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_data)
import calendar
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
	if '_' in filters.periodicity:
		filters.periodicity, filters.only = filters.periodicity.split("_")
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, 
		filters.periodicity, filters.accumulated_values, filters.company)

	income = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values, 
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)
		
	expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values, 
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)
	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)
	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)
	month_list = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
	def clean(*months):
		mlist = month_list[:]
		for month in months:
			if month in mlist:
				mlist.remove(month)
		return mlist

	rules = {
		'1': ('apr', 'jul', 'oct'),
		'2': ('jan', 'jul', 'oct'),
		'3': ('jan', 'apr', 'oct'),
		'4': ('jan', 'apr', 'jul'),
		'1,2': ('jul', 'oct'),
		'1,2,3': ('oct',)
	}
	rules.update({month: clean(month) for month in month_list})

	if filters.only:
		for i in range(len(data)):
			for only, months in rules.items():
				if filters.only == only:
					years = set(filters.from_fiscal_year.split("-")).union(filters.to_fiscal_year.split("-"))
					for month in months:
						for year in years:
							k = "_".join([month, year])
							if k in data[i]:
								data[i].pop(k)
								col = filter(lambda c: c.get('fieldname') == k, columns)
								if col:
									columns.remove(col[0])
							if 'total' in data[i]:
								data[i].pop('total')
								col = filter(lambda c: c.get('fieldname') == 'total', columns)
								if col:
									columns.remove(col[0])
	from shei.shei.report.sh_budget_variance_report.sh_budget_variance_report import get_data as bv_get_data


	filters['period'] = filters.periodicity
	filters['budget_against'] = "Cost Center"
	from shei.shei.report.sh_budget_variance_report.sh_budget_variance_report import get_columns as bv_get_columns
	bv_columns = [
		{'width': 150, 'fieldname': 'budget', 'fieldtype': 'Currency',
		 u'label': 'Budget 2018-2019'},
		{'width': 150, 'fieldname': 'difference', 'fieldtype': 'Currency',
		 u'label': 'Difference'},
		{'width': 150, 'fieldname': 'variance', 'fieldtype': 'Currency',
		 u'label': 'Varaiance 2018-2019'}
	]
	merged_columns = columns + bv_columns

	if filters.periodicity == 'Yearly' or (filters.periodicity == 'Monthly' and not filters.only):
		bv_data = bv_get_data(filters)
		for bv in bv_data:
			for d in data:
				if d.get("account") == bv[1]:
					d.budget = bv[2]
					d.difference = float(bv[3]) - float(d.get('oct_2019'))
					d.variance = bv[4]
					break
	elif filters.only in month_list:
		#  it will be easier to work with data coming from 'monthly' instead of rewritting the whole thing
		filters['period'] = 'Monthly'
		bv_data = bv_get_data(filters)
		get_budget_variance_for_given_month(filters, bv_data, data)
	elif filters.only in ['1', '2', '3', '4']:
		bv_data = bv_get_data(filters)
		# since the index is for a table, we need to remove 1 to access the right data.
		# As for the 3, it's because the data are coming in batch of 3.
		# This calculation also remove the first 2 data, if applicable, because they
		# are not used for the budget calculation
		index = (int(filters.only) * 3) - 1
		get_quaterly_budget_variance(index, bv_data, data)

	return merged_columns, data, None, chart

def get_quaterly_budget_variance(index, bv_data, data=[]):
	for bv in bv_data:
		for d in data:
			if d.get("account") == bv[1]:
				d.budget = bv[index]
				d.difference = bv[index + 1]
				d.variance = bv[index + 2]
				break


def get_budget_variance_for_given_month(filters, bv_data, data=[]):
	for bv in bv_data:
		for d in data:
			if d.get("account") == bv[1]:
				start_year = get_fiscal_year(date=filters.from_fiscal_year.split('-')[1], company=filters.company,
											 as_dict=True)
				nb_start_month = start_year['year_start_date'].month
				month_to_num = {name.lower(): num for num, name in enumerate(calendar.month_abbr) if num}
				nb_periodicity_month = month_to_num[filters.only]
				if nb_start_month <= nb_periodicity_month:  # selected month is this year
					time = nb_periodicity_month - nb_start_month
					starting_index = time + 2 # the 2 is to compensate for the 2 string at the start of the table
				else:
					remaining_time_bf_end_of_year = 12 - nb_start_month
					time = remaining_time_bf_end_of_year + nb_periodicity_month
					starting_index = int(time * 3) + 2 # the 2 is to compensate for the 2 string at the start of the table
				d.budget = bv[starting_index]
				d.difference = bv[starting_index + 1]
				d.variance = bv[starting_index + 2]
				break


def get_net_profit_loss(income, expense, period_list, company):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Net Profit / Loss") + "'",
		"account": "'" + _("Net Profit / Loss") + "'",
		"warn_if_negative": True,
		"currency": frappe.db.get_value("Company", company, "default_currency")
	}

	has_value = False

	for period in period_list:
		total_income = flt(income[-2][period.key], 3) if income else 0
		total_expense = flt(expense[-2][period.key], 3) if expense else 0

		net_profit_loss[period.key] = total_income - total_expense

		if net_profit_loss[period.key]:
			has_value=True

		total += flt(net_profit_loss[period.key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss


def get_chart_data(filters, columns, income, expense, net_profit_loss):
	x_intervals = ['x'] + [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	columns = [x_intervals]
	if income_data:
		columns.append(["Income"] + income_data)
	if expense_data:
		columns.append(["Expense"] + expense_data)
	if net_profit:
		columns.append(["Net Profit/Loss"] + net_profit)

	chart = {
		"data": {
			'x': 'x',
			'columns': columns,
			'colors': {
				'Income': '#5E64FF',
				'Expense': '#b8c2cc',
				'Net Profit/Loss': '#ff5858'
			}
		}
	}

	if not filters.accumulated_values:
		chart["chart_type"] = "bar"

	return chart
