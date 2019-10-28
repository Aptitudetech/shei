// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Profit and Loss Statement SHEI"] = $.extend({},
		erpnext.financial_statements);

	var periodicity = frappe.utils.filter_dict(frappe.query_reports['Profit and Loss Statement SHEI']['filters'], {'fieldname': 'periodicity'})[0];
	var today = new Date();
	var lastDayOfMonth = new Date(today.getFullYear(), today.getMonth()+1, 0);
	if(lastDayOfMonth.getDate() != today.getDate()){
		lastDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 0);
	}
	periodicity.options = [
		{'value': 'Monthly', 'label': __('Monthly')},
		{'value': 'Quarterly', 'label': __('Quarterly')},
		{'value': 'Half-Yearly', 'label': __('Half-Yearly')},
		{'value': 'Yearly', 'label': __('Yearly')},
		{'value': 'Monthly_jan', 'label': __('January')},
		{'value': 'Monthly_feb', 'label': __('February')},
		{'value': 'Monthly_mar', 'label': __('March')},
		{'value': 'Monthly_apr', 'label': __('April')},
		{'value': 'Monthly_may', 'label': __('May')},
		{'value': 'Monthly_jun', 'label': __('June')},
		{'value': 'Monthly_jul', 'label': __('July')},
		{'value': 'Monthly_aug', 'label': __('August')},
		{'value': 'Monthly_sep', 'label': __('September')},
		{'value': 'Monthly_oct', 'label': __('October')},
		{'value': 'Monthly_nov', 'label': __('November')},
		{'value': 'Monthly_dec', 'label': __('December')},
		{'value': 'Quarterly_1', 'label': __('1st Quarter')},
		{'value': 'Quarterly_2', 'label': __('2nd Quarter')},
		{'value': 'Quarterly_3', 'label': __('3rd Quarter')},
		{'value': 'Quarterly_4', 'label': __('Last Quarter')},
		{'value': 'Quarterly_1,2', 'label': __('1-2 Quarters')},
		{'value': 'Quarterly_1,2,3', 'label': __('1-3 Quarters')}
	];

	frappe.query_reports["Profit and Loss Statement SHEI"]["filters"].push(
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center"
		},
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		/**
                {
                        "fieldname":"quarter",
                        "label": __("Quarter"),
                        "fieldtype": "Select",
			"options": "\n1\n2\n3\n4\n1,2\n1,2,3",
			"depends_on": 'eval:cur_page.page.query_report.get_values().periodicity == "Quartely"'
                },
		**/
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "as_on",
			"label": __("As On"),
			"fieldtype": "Date",
			"default": lastDayOfMonth
			// "default": frappe.datetime.get_today()
		}
	);

});
