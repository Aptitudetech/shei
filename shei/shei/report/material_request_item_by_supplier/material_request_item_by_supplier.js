// Copyright (c) 2016, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.query_reports["Material Request Item by Supplier"] = {
	"filters": [
		{
                        "fieldname":"supplier",
                        "label": __("Supplier"),
                        "fieldtype": "Link",
                        "options": "Supplier",
                        "default": ""
                },
		{
                        "fieldname":"project",
                        "label": __("Project"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "default": ""
                }

	]
}
