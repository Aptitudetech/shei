// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

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

/*
frappe.ui.form.on("Price Configurator", "onload_post_render", function(frm, cdt, cdn){
    frappe.utils.filter_dict(cur_frm.fields_dict["price_configurator_items"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "item_discount_pourcent"})[0].read_only = true;
    cur_frm.fields_dict["price_configurator_items"].grid.grid_rows_by_docname[cdn].fields_dict["item_discount_pourcent"].refresh();
});*/

frappe.ui.form.on('Price Configurator', {
	refresh: function(frm) {
		/*frm.fields_dict.price_configurator_items.grid.get_selected_children().map(
			function(r){
				r.set_df_property("item_discount_pourcent","read_only",0);
				//r.toggle_enable(item_discount_pourcent, false)
		})*/
//cur_frm.toggle_enable(field_name, true)
	},
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
					'default_items': cur_frm.doc.pc_default_items,
				},
				freeze: true,
				freeze_message: "This operation may takes few minutes, please wait...",
				callback: function() {
					refresh_field("price_configurator_items");
					refresh_field("pc_default_items");
				}
		});
		reload();
	},
});
