// Copyright (c) 2016, Aptitude technologie and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Accounts Receivable SHEI"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"credit_days_based_on",
			"label": __("Credit Days Based On"),
			"fieldtype": "Select",
			"options": "\nFixed Days\nLast Day of the Next Month"
		},
		{
                        "fieldname":"currency",
                        "label": __("Currency"),
                        "fieldtype": "Link",
                        "options": "Currency"
                },
		{
                        "fieldname":"remove_advance_payment",
                        "label": __("Remove Advance Payment"),
                        "fieldtype": "Select",
                        "options": "\nyes"
                },
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"report_date",
			"label": __("As on Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nDue Date',
			"default": "Posting Date"
		},
		{
			"fieldname":"range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"reqd": 1
		},
		{
			"fieldname":"range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"reqd": 1
		},
		{
			"fieldname":"range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"reqd": 1
		}
	]
}
