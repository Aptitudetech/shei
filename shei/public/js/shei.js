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
		if(frm.doc.customer_deposit)
		{
			frappe.model.set_value(cdt, cdn, "naming_series", "PFI-");
			frappe.model.set_value(cdt, cdn, "quotation_mode", "Standard");
			frm.set_df_property('project', 'reqd', 1);
		}
		else
		{
			frappe.model.set_value(cdt, cdn, "naming_series", "QTN-");
			frappe.model.set_value(cdt, cdn, "quotation_mode", "Price Configurator");
			frm.set_df_property('project', 'reqd', 0);
		}
	},
	quotation_mode: function(frm, cdt, cdn) {
	    if(frm.doc.quotation_mode === 'Price Configurator'){
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

		if(frm.doc.quotation_mode === 'Price Configurator'){
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
				quotation_to: frm.doc.quotation_to,
				address: frm.doc.customer_address
			},
			callback: function(r) {
				if (r.message !== " ") {
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
	// display_lost_reason: function(frm){
    //     let dialog = new frappe.ui.Dialog({
	// 		title: __("Set as Lost"),
	// 		fields: [
	// 			{"fieldname": 'lost_reason', 'fieldtype': 'Link',  'options': 'Lost Reason', 'reqd': 1, label: __("Lost Reason")},
	// 			{'fieldname': 'other_reason', fieldtype: 'Small Text', label: __('Other Reason'), 'depends_on': "eval:doc.lost_reason === 'RL0008'"}
	// 		],
	// 		primary_action: function() {
	// 			var values = dialog.get_values();
	// 			let reason_description = frappe.db.get_value("Lost Reason", values["lost_reason"], 'lost_reason');
	//
	// 			reason_description.then(function(value){
	// 				let lost_reason = value['message']['lost_reason'];
	// 				let full_reason = lost_reason;
	// 				if(values["lost_reason"] == 'RL0008'){
	// 					if(values["other_reason"] == null ){
	// 						frappe.throw("You must write a reason before proceeding");
	// 					}
	// 					else{
	// 						full_reason = full_reason + " - " + values["other_reason"];
	// 					}
	// 				}
	// 				frm.call({
	// 					method: 'declare_order_lost',
	// 					doc: frm.doc,
	// 					args: {
	// 						'reason': full_reason
	// 					},
	// 					callback: function(r) {
	// 						dialog.hide();
	// 						frm.reload_doc();
	// 					},
	// 				});
	// 				refresh_field("quote_lost_reason");
	// 			});
	// 		},
	// 		primary_action_label: __('Declare Lost')
	// 	});
	//
	// 	dialog.show();
	// 	dialog.get_input('lost_reason').on('awesomplete-selectcomplete', function(e){
	// 		setTimeout(function(){
    //     			dialog.refresh();
    // 			}, 500);
	// 	});
    // }
});


//
// frappe.ui.form.on('Price Configurator Item', {
// 	before_panel_list_remove: function(frm, cdt, cdn) {
//    	    var deleted_row = frappe.get_doc(cdt, cdn);
// 	    var filtered = cur_frm.doc.items.filter(elem => elem['reference_panel'] == deleted_row['panel_id']);
// 	    filtered.forEach(function(element) {
// 		frappe.model.remove_from_locals('Quotation Item', element.name);
// 	    });
// 	    refresh_field("items");
// 	},
// 	aluminum_item: function(frm, cdt, cdn){
//         var d = locals[cdt][cdn];
//         if (!d.aluminum_item) return;
// 		if(d.panel_id == null || d.panel_id.value.length == 0){
// 			frappe.call({
// 				method: "shei.sheipy.set_panel_uuid",
// 				args:{},
//         		callback: function(r) {
// 				frappe.model.set_value(cdt, cdn, "panel_id", r.message);
// 			}
//       		})
// 	}
//     },
// });
//
//
// frappe.ui.form.on("Quotation Item", {
// 	item_code: function(frm, cdt, cdn) {
// 		var ct = locals[cdt][cdn];
// 		setTimeout(function(){
// 			frappe.call({
// 				method: "multilingual_extension.item_description.fetch_item_description",
// 				args:{
// 					party_name: frm.doc.party_name,
// 					quotation_to: frm.doc.quotation_to,
// 					item_code: ct.item_code,
// 					},
// 				callback: function(r) {
// 				frappe.model.set_value(cdt, cdn, "description", r.message);
// 				}
// 			})
// 		}, 1000);
// 	}
// });
//
//
//Will overwrite the QuotationController - used to change 'Set as lost' button behavior
// erpnext.selling.CustomQuotationController = erpnext.selling.QuotationController.extend({
//     refresh: function(doc, dt, dn) {
// 		this._super(doc, dt, dn);
// 		//the button should only be available if the quote is 'Submit'
// 		if(doc.docstatus == 1 && doc.status!=='Lost') {
// 			if(doc.status!=="Ordered") {
// 				this.frm.remove_custom_button(__('Set as Lost'));
// 				this.frm.add_custom_button(__('Set as Lost'), () => {
// 					this.frm.trigger('display_lost_reason');
// 				});
// 			}
// 		}
// 	}
// });
//
// cur_frm.script_manager.make(erpnext.selling.CustomQuotationController);


//Sales Invoice
frappe.ui.form.on("Sales Invoice Credit Notes", "credits_remove", function(frm, cdt, cdn){
    frm.doc.total_credits = 0.0;
    frm.doc.credits.forEach(function(row){
      frm.doc.total_credits += row.allocated_amount;
    });
    frm.refresh_field("total_credits");
});

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
frappe.ui.form.on('Project', {
    update_task_order: function(frm) {
        var tasks = cur_frm.doc.tasks;
		tasks.forEach(function(element) {
			element.task_order = element.idx;
        });
		frappe.msgprint("Please save the document to apply the changes");
    },
	date_ready_for_production: function(frm, cdt, cdn){
        if (!frm.doc.date_ready_for_production) return;
		if(!frm.doc.expected_end_date){
			var exp_end_date = frappe.datetime.add_days(frm.doc.date_ready_for_production, 42);
	        frappe.model.set_value(cdt, cdn, 'expected_end_date', exp_end_date);
		}
    },
	onload: function(frm, cdt, cdn) {
		frappe.call({
			method: "shei.sheipy.on_project_onload",
			args: {
				project_name: frm.doc.name,
			},
			callback: function (r) {
				frm.doc.project_amount_from_so = r.message;
				frm.refresh_field("project_amount_from_so");
				frm.refresh_field("tasks");
				frm.doc.__unsaved = false;
				frm.toolbar.refresh();
			}
		});
	},
	customer: function(frm, cdt, cdn) {
		if (frm.doc.customer) {
			frappe.call({
				method: "shei.sheipy.get_sales_person_from_customer",
				args: {
					dt: cdt,
					customer_name: frm.doc.customer,
					project: frm.doc.name,
				},
				callback: function (r) {
				}
			});
			frappe.call({
				method: "shei.sheipy.change_project_name",
				args: {
					dt: cdt,
					project_name: frm.doc.name,
					customer_name: frm.doc.customer,
				},
				callback: function (r) {
					if (r.message) {
						frappe.set_route("Form", "Project", r.message);
					}
				}
			});
		}
	},
	refresh: function(frm, cdt, cdn) {
		if (frm.doc.sub_type) {
			frm.add_custom_button(__("Get Tasks from template"), function () {
				frappe.call({
					'method': 'shei.shei.doctype.task_template.task_template.get_all_task_template_from_sub_type',
					'args': {
						'sub_type': frm.doc.sub_type
					},
					'callback': function (res) {
						var tasks = cur_frm.doc.tasks;
						var task_order = tasks.length + 1;
						res.message.forEach(function (element) {
							cur_frm.add_child("tasks", {
								'title': element.name,
								'status': 'Open',
								'assigned_to': element.assigned_to,
								'task_order': task_order,
								'idx': task_order
							});
							task_order++;
						});
						refresh_field("tasks");
					}
				});
			});
		}
	}
});

//
//
// frappe.ui.form.on('Project Task', {
//     status: function(frm, cdt, cdn){
//         var d = locals[cdt][cdn];
//         if (!d.status) return;
// 	if(d.status == "Closed"){
// 	        frappe.model.set_value(cdt, cdn, 'end_date', frappe.datetime.get_today());
// 	}
//     }
// });
//
// frappe.ui.form.on('Crate Information', {
//     crate_gross_weight: function(frm, cdt, cdn){
//         var d = locals[cdt][cdn];
//         if (!d.crate_gross_weight) return;
//         frappe.model.set_value(cdt, cdn, 'crate_net_weight', d.crate_gross_weight - 100);
//     }
// });

//Customer
frappe.ui.form.on("Customer", {
	refresh: function() {
		cur_frm.add_custom_button("Sales History", function () {
			frappe.route_options = {'customer': cur_frm.doc.name};
			frappe.set_route("List", "Sales History");
		});
	},
	default_currency: function(frm, cdt, cdn) {
		if (frm.doc.default_currency === "USD") {
			frm.doc.accounts = [];
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Bank Account by Currency',
					fieldname: ['name','bank_account'],
					filters: {'parenttype': 'Bank Account Setup', 'currency': frm.doc.default_currency},
					parent: 'Bank Account Setup'
				},
				callback: function(r){
					var row = frappe.model.add_child(cur_frm.doc, "Party Account", "accounts");
					row.company = frappe.defaults.get_default("Company");
					if(r.message.bank_account) {
						row.account = r.message.bank_account
			 		}
					refresh_field("accounts");
				}
			});
		} else {
			frm.doc.accounts = [];
		}
	},
});



// $.extend(erpnext.utils, {
//         set_party_dashboard_indicators: function(frm){
//                 if (frm.doc.__onload && frm.doc.__onload.dashboard_info){
//                         var info = frm.doc.__onload.dashboard_info;
//                         frm.dashboard.add_indicator(__('Last Year Billing: {0}',
//                                 [format_currency(info.billing_last_year, info.currency)]), 'blue')
// 			frm.dashboard.add_indicator(__('This Year Billing: {0}',
//                                 [format_currency(info.billing_this_year, info.currency)]), 'blue')
//                         frm.dashboard.add_indicator(__('Total Unpaid: {0}',
//                                 [format_currency(info.total_unpaid, info.currency)]),
//                                 info.total_unpaid ? 'orange': 'green');
//                 }
//         }
// });

// Sales Order
frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
		  frm.add_custom_button(__('Work Order'), function(){
			var checked_items =  cur_frm.fields_dict.items.grid.get_selected_children().map(function(r){return r}); //list all checked instance
			frappe.call({
				method: 'shei.events.create_work_order',
				args: {
					mfg_items : checked_items,
					so_name : frm.docname,
				},
				callback: function() { }
			});

		}, __("Make"));
		frm.add_custom_button(__('Latest Work Order'), function(){
			var checked_items =  cur_frm.fields_dict.items.grid.get_selected_children().map(function(r){return r}); //list all checked instance
			frappe.call({
				method: 'shei.events.update_work_order',
				args: {
					mfg_items : checked_items,
					so_name : frm.docname,
					work_order_name: cur_frm.doc.work_orders[cur_frm.doc.work_orders.length - 1].link_name,
				},
				callback: function() { }
			});
		}, __("Update"));
  	},
	customer: function(frm, cdt, cdn) {
    	if (!frm.doc.customer){
			frappe.call({
				method: "multilingual_extension.get_terms_and_conditions.get_terms_and_conditions",
				args:{
					party_name: frm.doc.customer,
					quotation_to: "Customer",
					address: frm.doc.customer_address
				},
				callback: function(r) {
					if (r.message !== " ") {
						frappe.model.set_value(cdt, cdn, "tc_name", r.message);
					}
				}
			});
		}
	}
});

// Bank Account
frappe.ui.form.on('Bank Account', {
	refresh: function(frm) {
		frm.set_query('deposit_account', function (doc) {
			return {
				'filters': {
					'company': frm.doc.company
				}
			}
		})
	}
});
// Suppplier
// $.extend(erpnext.utils, {
//         set_party_dashboard_indicators: function(frm){
//                 if (frm.doc.__onload && frm.doc.__onload.dashboard_info){
//                         var info = frm.doc.__onload.dashboard_info;
//                         frm.dashboard.add_indicator(__('Last Year Billing: {0}',
//                                 [format_currency(info.billing_last_year, info.currency)]), 'blue')
// 			frm.dashboard.add_indicator(__('This Year Billing: {0}',
//                                 [format_currency(info.billing_this_year, info.currency)]), 'blue')
//                         frm.dashboard.add_indicator(__('Total Unpaid: {0}',
//                                 [format_currency(info.total_unpaid, info.currency)]),
//                                 info.total_unpaid ? 'orange': 'green');
//                 }
//         }
// });

// Stock entry
frappe.ui.form.on("Stock Entry", {
	refresh: function(frm, cdt, cdn) {
		frm.add_custom_button(__("Get Items from Sales Order"), function () {
			if (frm.doc.from_warehouse && frm.doc.to_warehouse && (frm.doc.purpose == "Material Transfer")) {
				frappe.call({
					method: "shei.sheipy.fetch_items_from_so",
					args: {
						so: frm.doc.sales_order,
					},
					callback: function (r) {
						if (!r.message) {
							frappe.throw(__("Sales Order does not contain any stock item"))
						} else {
							$.each(r.message, function (item, value) {
								var d = frappe.model.add_child(cur_frm.doc, "Stock Entry Detail", "items");
								d.item_code = item;
								d.s_warehouse = frm.doc.from_warehouse;
								d.t_warehouse = frm.doc.to_warehouse;
								d.qty = value;
								d.uom = 'Unit';
								d.conversion_factor = 1;
								d.transfer_qty = value;
							});
						}
						frm.refresh_field("items");
					}
				});
			} else {
				msgprint("From and To warehouses are mandatory and Purpose must be Material Transfer");
			}
		});
	}
});
// Purchase Invoice
frappe.ui.form.on("Purchase Invoice", {
	bill_date: function(frm, cdt, cdn) {
		if (frm.doc.bill_date) {
			frappe.call({
				method: "shei.sheipy.get_due_date",
				args: {
					supplier: frm.doc.supplier,
					bill_date: frm.doc.bill_date
				},
				callback: function (r) {
					if (r.message) {
						cur_frm.set_value("due_date", new Date(r.message));
					}
				}
			});
		}
	}
});
// Payment Entry
frappe.ui.form.on("Payment Entry", {
	refresh: function(frm, cdt, cdn) {
		frm.add_custom_button(__("Reserve cheque number"), function () {
			if (frm.doc.mode_of_payment == "Cheque CDN" || frm.doc.mode_of_payment == "Cheque USD") {
				frappe.call({
					method: "shei.advance_payment.get_cheque_series",
					args: {
						account: frm.doc.paid_from,
					},
					callback: function (r) {
						frappe.model.set_value(cdt, cdn, "reference_no", r.message);
					}
				});
			} else {
				msgprint("You must select 'cheque' as a mode of payment to use this button");
			}
		});
	}
});

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

