// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Balance Sheet SHEI"] = erpnext.financial_statements;

	frappe.query_reports["Balance Sheet SHEI"]["filters"].push(
                {
                        "fieldname":"quarter",
                        "label": __("Quarter"),
                        "fieldtype": "Select",
                        "options": "\n1\n2\n3\n4\n1,2\n1,2,3"
                },
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check",
			"default": 0
		}
	);
});


