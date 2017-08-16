// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Profit and Loss Statement SHEI"] = $.extend({},
		erpnext.financial_statements);

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
                {
                        "fieldname":"quarter",
                        "label": __("Quarter"),
                        "fieldtype": "Select",
			"options": "\n1\n2\n3\n4\n1,2\n1,2,3"
                },
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		}
	);
});
