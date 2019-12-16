//Address
frappe.ui.form.on("Address", "refresh", function(frm, cdt, cdn) {
	if (frm.doc.__islocal){
		setTimeout(function(){
			frappe.model.set_value(cdt, cdn, "country", "");
		}, 1500);
	}
});


//Quotation
frappe.ui.form.on('Quotation', {
	customer_deposit: function(frm, cdt, cdn) {
		if(frm.doc.customer_deposit){
			frm.set_df_property('project', 'reqd', 1);
		}
       	 	else{
			frm.set_df_property('project', 'reqd', 0);
		}
	},
	quotation_mode: function(frm, cdt, cdn) {
	    if(frm.doc.quotation_mode == 'Price Configurator'){
			frm.set_df_property('items', 'reqd', 0);
			frm.set_df_property('measurement', 'reqd', 1);
	    }
		else{
			frm.set_df_property('items', 'reqd', 1);
			frm.set_df_property('measurement', 'reqd', 0);
	    }
	},
	total_av_nuts: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        if (!d.total_av_nuts) return;
   	    frappe.model.set_value(cdt, cdn, "total_tools", 1);
	    refresh_field("total_tools");
	},
	customer_deposit: function(frm, cdt, cdn) {
		if(frm.doc.customer_deposit == 1)
		{
			frappe.model.set_value(cdt, cdn, "naming_series", "PFI-");
			frappe.model.set_value(cdt, cdn, "quotation_mode", "Standard");
		}
		else
		{
			frappe.model.set_value(cdt, cdn, "naming_series", "QTN-");
			frappe.model.set_value(cdt, cdn, "quotation_mode", "Price Configurator");
		}
	},
	refresh: function(frm, cdt, cdn) {
		frappe.call({
			method: "shei.sheipy.set_price_configurator_item_selects",
			args: {
				dt: 'Price Configurator Item',
			},
			callback: function(r) {
				var back = frappe.meta.get_docfield("Price Configurator Item","back", cur_frm.doc.name);
				back.options = r['message'][0]['backs'];
				var cut = frappe.meta.get_docfield("Price Configurator Item","cut", cur_frm.doc.name);
				cut.options = r['message'][0]['cuts'];
				var thickness = frappe.meta.get_docfield("Price Configurator Item","thickness", cur_frm.doc.name);
				thickness.options = r['message'][0]['thickness'];
				}
		});

		if(frm.doc.quotation_mode == 'Price Configurator'){
			frm.set_df_property('items', 'reqd', 0);
			frm.set_df_property('measurement', 'reqd', 1);
		}
		else{
			frm.set_df_property('items', 'reqd', 1);
			frm.set_df_property('measurement', 'reqd', 0);
		}

		frm.add_custom_button(__("Update Item Description"), function() {
			frappe.call({
				method: "multilingual_extension.item_description.update_item_description",
				args: {
					customer: frm.doc.party_name,
					docType: "Quotation",
					docName: frm.doc.name,
				},
					callback: function(r) {
					cur_frm.reload_doc();
					}
			})
		});
	},
	party_name: function(frm, cdt, cdn) {
		frappe.call({
			method: "multilingual_extension.get_terms_and_conditions.get_terms_and_conditions",
			args:{
				party_name: frm.doc.party_name,
				quotation_to: frm.doc.quotation_to
			},
			callback: function(r) {
				if (r.message != " ") {
					frappe.model.set_value(cdt, cdn, "tc_name", r.message);
				}
			}
		});
	},
	on_submit: function(frm, cdt, cdn){
		if (frm.doc.customer_deposit && frm.doc.project) {
			frappe.call({
				method: "shei.sheipy.set_project_pfi",
				args:{
					pfi: frm.doc.name,
					action: "add"
				},
				callback: function(r) {}
			});
		}
		if (frm.doc.customer_deposit && !frm.doc.project) {
			frappe.throw(__("Project is mandatory when Customer Deposit is selected"));
		}
	},
	after_cancel: function(frm, cdt, cdn){
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
	},

});

//Sales Invoice
frappe.ui.form.on("Sales Invoice", {
	refresh: function(frm, cdt, cdn) {
		frm.add_custom_button(__("Update Item Description"), function () {
			frappe.call({
				method: "multilingual_extension.item_description.update_item_description",
				args: {
					customer: frm.doc.customer,
					docType: "Sales Invoice",
					docName: frm.doc.name,
				},
				callback: function (r) {
					cur_frm.reload_doc();
				}
			})
		});
	},
	get_credit_notes: function(frm, cdt, cdn) {
		if (frm.doc.customer) {
			return frm.call({
				"method": "shei.events.get_credit_notes",
				"args": {
					"doctype": frm.doctype,
					"party_type": "customer",
					"party_name": frm.doc.customer
				},
				"callback": function (res) {
					console.log(res);
					if (res && res.message) {
						frm.clear_table('credits');
						var pending_amount = frm.doc.outstanding_amount, credits = 0.0;
						res.message.forEach(function (row) {
							var d = frm.add_child('credits', row);
							if (d.allocated_amount > pending_amount) {
								frappe.model.set_value(d.doctype, d.name,
									'allocated_amount', pending_amount);
							}
							pending_amount - d.allocated_amount;
							credits += d.allocated_amount;
						});
						frm.refresh_field("credits");
						frm.set_value("total_credits", credits);
					}
				}
			});
		}
	},
	on_submit: function(frm, cdt, cdn) {
		frm.reload_doc();
	}
});

//Project
//Customer
// Sales Order
// Delivery note
// Bank Account
// Suppplier
// Terms and condition
// Stock entry
// Purchase Invoice
// Payment Entry


//Global
frappe.ui.form.AssignToDialog = frappe.ui.form.AssignToDialog.extend({
    init: function(opts){
       console.log("Reach2");
		var me = this;
		var dialog = new frappe.ui.Dialog({
			title: __('Add to To Do'),
			fields: [
				{ fieldtype: 'Link', fieldname: 'assign_to', options: 'User', label: __("Assign To"), reqd: false, filters: { 'user_type': 'System User' }},
				{ fieldtype: 'Button', fieldname: 'add_user', label: __("Add User")},
				{ fieldtype: 'Small Text', fieldname: 'user_list', label: __("Assign to These Users")},
				{ fieldtype: 'Check', fieldname: 'myself', label: __("Assign to me"), "default": 0 },
				{ fieldtype: 'Small Text', fieldname: 'description', label: __("Comment") },
				{ fieldtype: 'Section Break' },
				{ fieldtype: 'Column Break' },
				{ fieldtype: 'Date', fieldname: 'date', label: __("Complete By") },
				{ fieldtype: 'Check', fieldname: 'notify', label: __("Notify by Email"), default: 1},
				{ fieldtype: 'Column Break' },
				{ fieldtype: 'Select', fieldname: 'priority', label: __("Priority"),
					options: [
						{ value: 'Low', label: __('Low') },
						{ value: 'Medium', label: __('Medium') },
						{ value: 'High', label: __('High') }
					],
					// Pick up priority from the source document, if it exists and is available in ToDo
					'default': ["Low", "Medium", "High"].includes(opts.obj.frm && opts.obj.frm.doc.priority
						? opts.obj.frm.doc.priority : 'Medium')
				},
			],
			primary_action: function() {
				frappe.ui.add_assignment(opts, this);
			},
			primary_action_label: __("Add")
		});
		dialog.fields_dict.add_user.input.onclick = function() {
			dialog.fields_dict.user_list.set_value(
				dialog.fields_dict.user_list.get_value()
				+ dialog.fields_dict.assign_to.get_value()
				+ ";"
			);
			dialog.fields_dict.assign_to.set_value("");
		};
		$.extend(me, dialog);
		me.dialog = dialog;
		me.dialog.fields_dict.assign_to.get_query = "frappe.core.doctype.user.user.user_query";
		var myself = me.dialog.get_input("myself").on("click", function() {
			me.toggle_myself(this);
		});
		me.toggle_myself(myself);
    },
});

frappe.ui.add_assignment = function(opts, dialog) {
	users = dialog.fields_dict.user_list.get_value().split(';');
	users.forEach(function(assign_to) {
		var args = dialog.get_values();
		if(args && assign_to) {
			return frappe.call({
				method: opts.method,
				args: $.extend(args, {
					doctype: opts.doctype,
					name: opts.docname,
					assign_to: assign_to,
					bulk_assign:  opts.bulk_assign || false,
					re_assign: opts.re_assign || false
				}),
				callback: function(r,rt) {
					if(!r.exc) {
						if(opts.callback){
							opts.callback(r);
						}
						dialog && dialog.hide();
					}
				},
				btn: this
			});
		}
	});
};

