// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Configurator', {
	test: function(frm) {
			frappe.call({
					method: "test",
					doc: frm.doc,
					args: {
					},
			callback: function() {
					}
			});
	},
});

frappe.ui.form.on('Product Configurator', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Product Configurator', {
	calculate_final_price: function(frm) {
			if (frm.doc.__unsaved){
				frappe.throw(__("Please save the document before proceeding"));
			}
			frappe.call({
					method: "calculate_final_price",
					doc: frm.doc,
					args: {
					},
					freeze: true,
					freeze_message: "This operation may takes few minutes, please wait...",
			callback: function() {
					}
			});
			reload();
	},
});
