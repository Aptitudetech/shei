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

frappe.ui.form.on('Task Progression Range', "task_subject", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (!d.task_subject) return;
	frappe.db.get_value('Task Template', d.task_subject, 'task_order', function(r){
		if(r.task_order) {
		        frappe.model.set_value(cdt, cdn, 'task_order', r.task_order);
		}
	});
	refresh_field("task_order");
});
