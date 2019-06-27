// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Configurator', {
	onload: function(frm){
		if (frappe.user.has_role("System Manager")){
			var item_discount = frappe.meta.get_docfield("Price Configurator Item", "discount_pourcent", cur_frm.doc.name);
			item_discount.read_only = 0;
			var price_line = frappe.meta.get_docfield("Price Configurator Item", "line_price_customer_currency", cur_frm.doc.name);
			price_line.read_only = 0;	
		}
	},
	refresh: function(frm) {
	},
	test: function(frm) {
		frappe.call({
				method: "test",
				doc: frm.doc,
				args: {
				},
		callback: function(content){
			}
		});
	},
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
					refresh_field("price_configurator_items");
					frm.reload_doc();
				}
			});
	},
	pc_add_items: function(frm) {
		frappe.call({
				method: "pc_add_items",
				doc: frm.doc,
				args: {
					'default_items': cur_frm.doc.pc_default_items,
				},
				freeze: true,
				freeze_message: "This operation may takes few minutes, please wait...",
				callback: function() {
					refresh_field("price_configurator_items");
					refresh_field("pc_default_items");
				}
		});
	},
});
