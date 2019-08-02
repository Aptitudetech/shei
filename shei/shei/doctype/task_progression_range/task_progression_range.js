// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Progression Range', {
	refresh: function(frm) {
		cur_frm.set_query("task_subject", function() {
        		return {
            			"filters": {
	                		"sub_type": frm.doc.sub_type
            			}
        		};
		});
	}
});

