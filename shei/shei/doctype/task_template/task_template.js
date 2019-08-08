// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Template', {
	refresh: function(frm) {
		frm.disable_save();
	},
	update_task_progression_range_order: function(frm) {
                frappe.call({
                                method: "update_task_template",
                                doc: frm.doc,
                                args: {
                                },
                                freeze: true,
                                freeze_message: "This operation may takes few minutes, please wait...",
                        callback: function() {
                        }
                });
        },

});
