// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Subject', {
	refresh: function(frm) {
		frm.disable_save();
	},
	btn_update_task_info: function(frm) {
                frappe.call({
                                method: "update_task_info",
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

//will fetch the last task_order from the curr sub_type and add 1
frappe.ui.form.on("Task Subject", "sub_type", function(frm, cdt, cdn) {
		frappe.call({
			'method': 'frappe.client.get_list',
			'args': {
				'doctype': 'Task Subject',
				'fields': ['task_order'],
				'filters': {'disabled': 0, 'sub_type':frm.doc.sub_type},
				'order_by': 'task_order desc',
				'limit_page_length': 1
			},
			'callback': function(res){
				var frm = cur_frm;
				if (res && res.message){
					frappe.model.set_value(cdt, cdn, "task_order", parseInt(res.message[0]['task_order']) + 1);
				}
		}
	});
});
