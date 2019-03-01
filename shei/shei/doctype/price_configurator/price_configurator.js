// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Configurator', {
	refresh: function(frm) {

	}
});
// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Configurator', {
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

/*frappe.ui.form.on("Price Configurator", "onload", function(frm) {
	frm.fields_dict.price_configurator_items.grid.get_field('back_finish').get_query =
		function() {
			return {
				query: "shei.shei.doctype.price_configurator.price_configurator.filter_back",
				filters: {
					"product":cur_frm.doc.client
				}
			}
		}
});*/

frappe.ui.form.on('Price Configurator', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Price Configurator', {
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
	pc_add_items: function(frm) {
		frappe.call({
				method: "pc_add_items",
				doc: frm.doc,
				args: {
					'default_items': cur_frm.fields_dict.pc_default_items.grid.docfields
				},
				freeze: true,
				freeze_message: "This operation may takes few minutes, please wait...",
		callback: function() {
				}
		});
		reload();
},
});
