// Copyright (c) 2016, Aptitude technologie and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Graphic Project Analysis"] = {
	"filters": [
		{
			"fieldname": "from_expected_start_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_expected_start_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
                        "fieldname": "status",
                        "label": __("Status"),
                        "fieldtype": "Select",
			"options" : "\nOpen\nCompleted\nTemplate\nStock purchase\nMarketing Projects",
			"default": "Completed",
                },
	],
	"formatter":
		function (value, row, column, data, default_formatter){
	        if (column['content'] == "Fabrication Time"){
		        if (data['Fabrication Time'] > 20){
		             value = "<span style='color:red!important;font-weight:bold;'>" + value + "</span>";
			}
		}
		if (column['content'] == "Printing Time"){
                        if (data['Printing Time'] > 20){
                             value = "<span style='color:orange!important;font-weight:bold;'>" + value + "</span>";
                        }
                }
		if (column.fieldtype == "Link"){
 			value = `<a href='#Form/${column.options}/${value}' target='blank'>${value}</a>`;
		}
		if (value == null){ //without this condition, it will print 'null' on the report
			value = ""
		}
		return value;
	}
};
