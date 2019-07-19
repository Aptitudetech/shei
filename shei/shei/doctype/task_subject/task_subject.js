// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Subject', {
	refresh: function(frm) {
		frm.disable_save();
	},
	btn_update_task_info: function(frm) {
                frappe.call({
                                method: "update_task_information",
                                doc: frm.doc,
                                args: {
                                },
                                freeze: true,
                                        freeze_message: "This operation may takes few minutes, please wait...",
                        callback: function() {
				var sub_type = frm.doc.sub_type;
				var task_desc = frm.doc.task_desc;
				var path = (sub_type + '-' + task_desc).toUpperCase();
				frappe.set_route("Form", "Task Subject", path);
                        }
                });
        },
});
