frappe.ui.form.on(cur_frm.doctype, {
    display_lost_reason: function(frm){
        let dialog = new frappe.ui.Dialog({
			title: __("Set as Lost"),
			fields: [
                                {"fieldname": 'lost_reason', 'fieldtype': 'Link',  'options': 'Lost Reason', 'reqd': 1},
				{'fieldname': 'other_reason', fieldtype: 'Small Text', label: __('Other Reason'), 'depends_on': "eval:doc.lost_reason === 'RL0008'"}
			],
			primary_action: function() {
				var values = dialog.get_values();
				let reason_description = frappe.db.get_value("Lost Reason", values["lost_reason"], 'lost_reason');
				
				reason_description.then(function(value){
					let lost_reason = value['message']['lost_reason']
					let full_reason = lost_reason;
					if(values["lost_reason"] == 'RL0008'){
						if(values["other_reason"] == null ){
							frappe.throw("You must write a reason before proceeding");
						}
						else{
							full_reason = full_reason + " - " + values["other_reason"];
						}
					}
					frm.call({
						method: 'declare_order_lost',
						doc: frm.doc,
						args: {
							'reason': full_reason
						},
						callback: function(r) {
							dialog.hide();
							frm.reload_doc();
						},
					});
					refresh_field("quote_lost_reason");
				});
			},
			primary_action_label: __('Declare Lost')
		});

		dialog.show();
		dialog.get_input('lost_reason').on('awesomplete-selectcomplete', function(e){
			setTimeout(function(){
        			dialog.refresh();
    			}, 500);
		});
    }
});

//Will overwrite the QuotationController - used to change 'Set as lost' button behavior
erpnext.selling.CustomQuotationController = erpnext.selling.QuotationController.extend({
    refresh: function(doc, dt, dn) {
		this._super(doc, dt, dn);
		//the button should only be available if the quote is 'Submit'
		if(doc.docstatus == 1 && doc.status!=='Lost') {
			if(doc.status!=="Ordered") {
				this.frm.remove_custom_button(__('Set as Lost'));
				this.frm.add_custom_button(__('Set as Lost'), () => {
					this.frm.trigger('display_lost_reason');
				});
			}
		}
	}
});
cur_frm.script_manager.make(erpnext.selling.CustomQuotationController);

/* frappe.ui.form.on('Quotation', 'refresh', function(frm, cdt, cdn){
	if (!frm.doc.__islocal){
		dashboard_link_doctype(frm, 'Product Configurator', __('Sales Order'), {  //sales order = where the link should be displayed
			'fieldname': 'quote',
			'transactions': [
				{
					'items': ['Product Configurator'],
					'label': __('Product Configurator')
				}]
		});
	}
});

function dashboard_link_doctype(frm, doctype, section, links){
	debugger;
	var parent = $(format('.form-dashboard-wrapper h6:contains("{}")', [section])).parent();
	parent.find(format('div.document-link[data-doctype="{}"]', [doctype])).remove();
	parent.append(frappe.render_template('dashboard_link_doctype', {'doctype': doctype}));
	var self = parent.find(format('div.document-link[data-doctype="{}"]', [doctype]));
	set_open_count(frm, doctype, links);
	// bind links
	self.find('.badge-link').on('click', function(){
		var routes = {};
		routes[frappe.scrub(frm.doc.doctype)] = frm.doc.name;
		frappe.route_options = routes;
		frappe.set_route('List', doctype);
	});

	// bind open notifications
	self.find('.open-notification').on('click', function() {
		frappe.route_options = {
			'product_configurator': frm.doc.name//,
			//'status': 'Draft'
		};
		frappe.set_route('List', doctype);
	});
}

function set_open_count (frm, doctype, links){
	frappe.call({
		'method': 'shei.api.get_open_count',
		'args': {
			'doctype': frm.doctype,
			'name': frm.docname,
			'links': links
		},
		'callback': function(res){
			// update badges
			if (res && res.message){
				res.message.count.forEach(function(d){
					frm.dashboard.set_badge_count(
						d.name, cint(d.open_count), cint(d.count)
					);
				});
			}
		}
	});
}
*/







    frappe.ui.form.on("Quotation", "customer_deposit", function(frm, cdt, cdn) {
	if(frm.doc.customer_deposit == 1)
		{
		frappe.model.set_value(cdt, cdn, "naming_series", "PFI-");
	}
	else
		{
		frappe.model.set_value(cdt, cdn, "naming_series", "QTN-");
	}
});

frappe.ui.form.on("Quotation", "customer", function(frm, cdt, cdn) {
	frappe.db.get_value("Customer", frm.doc.customer, "tc_name", function(r){
		if(r.tc_name) {
			frappe.model.set_value(cdt, cdn, "tc_name", r.tc_name);			
		}
	});
	refresh_field("tc_name");
}); 

frappe.ui.form.on("Quotation", "refresh", function(frm, cdt, cdn) {

        frm.add_custom_button(__("Update Item Description"), function() {
		frappe.call({
			method: "multilingual_extension.item_description.update_item_description",
			args: {
				customer: frm.doc.customer,
				docType: "Quotation",
				docName: frm.doc.name,
			},
	    		callback: function(r) {
				cur_frm.reload_doc();
      			}
		})
	});
});

//frappe.ui.form.on("Quotation Item", "item_code", function(frm, cdt, cdn) {
//	ct = locals[cdt][cdn]
//	frappe.after_ajax(function() {
//		frappe.call({
//			method: "multilingual_extension.item_description.fetch_item_description",
//			args:{
//				customer_code: frm.doc.customer,
//				item_code: ct.item_code,
//				},
//            	callback: function(r) {
//			frappe.model.set_value(cdt, cdn, "description", r.message);
//			}
//        	})
//	});
//});

//frappe.ui.form.on("Quotation", "customer", function(frm, cdt, cdn) {
//		frappe.call({
//			method: "multilingual_extension.get_terms_and_conditions.get_terms_and_conditions",
//			args:{
//				customer_code: frm.doc.customer
//				},
//            	callback: function(r) {
//			if (r.message != " ") {
//				frappe.model.set_value(cdt, cdn, "tc_name", r.message);
//			}
//        	    }
//	});
//});

//frappe.ui.form.on("Quotation", "validate", function(frm, cdt, cdn){
//	if (frm.doc.customer_deposit && !frm.doc.project) {
//		msgprint(__("Project is mandatory when Customer Deposit is selected"));
//		validated = false;
//	}
//});

frappe.ui.form.on("Quotation", "on_submit", function(frm, cdt, cdn){
	if (frm.doc.customer_deposit && frm.doc.project) {
		frappe.call({
			method: "shei.sheipy.set_project_pfi",
			args:{
				pfi: frm.doc.name,
				action: "add"
			},
	            	callback: function(r) {
	        	}
		});
	}
	if (frm.doc.customer_deposit && !frm.doc.project) {
		frappe.throw(__("Project is mandatory when Customer Deposit is selected"));
	}
});

frappe.ui.form.on("Quotation", "after_cancel", function(frm, cdt, cdn){
	if (frm.doc.customer_deposit && frm.doc.project) {
		frappe.call({
			method: "shei.sheipy.set_project_pfi",
			args:{
				pfi: frm.doc.name,
				action: "remove"
			},
	            	callback: function(r) {
	        	}
		});
	}
});