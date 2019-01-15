// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

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

frappe.ui.form.on('Product Configurator', {
	refresh: function(frm) {
		if (cur_frm.doc.is_published == true){
			cur_frm.page.add_menu_item("Remove the access to this file to the client",unpublish_document(cur_frm.doc.name, cur_frm.doc.pc_user_email));
		}
		else{
			cur_frm.page.add_menu_item("Send price to the client",publish_document(cur_frm.doc.name, cur_frm.doc.pc_user_email));
		}
	}
});



function unpublish_document(doc_name, user_email){
	return function(){
		var d = new frappe.ui.Dialog({
				'fields': [
						{'fieldname': 'ht', 'fieldtype': 'HTML'},
				],
				primary_action: function(frm){
						d.hide();
						frappe.call({
								method: "shei.shei.doctype.product_configurator.product_configurator.unpublish_document",
								args: {
										"doc_name": doc_name,
										"email": user_email,
								},
								callback: function() { }
						 });
				}
		});
		d.fields_dict.ht.$wrapper.html('Are you sure you want to stop sharing this document with the client?');
		d.show();
	}
}


function publish_document(doc_name, user_email){
	return function(){
		var d = new frappe.ui.Dialog({
				'fields': [
						{'fieldname': 'ht', 'fieldtype': 'HTML'},
				],
				primary_action: function(frm){
						d.hide();
						frappe.call({
								method: "shei.shei.doctype.product_configurator.product_configurator.publish_document",
								args: {
										"doc_name": doc_name,
										"email": user_email,
								},
								callback: function() { }
						 });
				}
		});
		d.fields_dict.ht.$wrapper.html('Are you sure you want to send this file to the client?');
		d.show();
	}
}
