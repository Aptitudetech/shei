erpnext.accounts.SalesInvoiceController = erpnext.accounts.SalesInvoiceController.extend({
	"get_credit_notes": function(frm){
	if (frm.doc.customer){
		return frm.call({
			"method": "shei.events.get_credit_notes",
			"args": {
				"doctype": frm.doctype,
				"party_type": "customer",
				"party_name": frm.doc.customer
			},
			"callback": function(res){
				if (res && res.message){
					frm.clear_table('credits');
					var pending_amount = frm.doc.outstanding_amount, credits = 0.0;
					res.message.forEach(function(row){
						var d = frm.add_child('credits', row);
						if (d.allocated_amount > pending_amount){
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
	}
});

$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));

$.extend(erpnext.utils, {
	set_party_dashboard_indicators: function(frm){
		if (frm.doc.__onload && frm.doc.__onload.dashboard_info){
			var info = frm.doc.__onload.dashboard_info;
			frm.dashboard_info.add_indicator(__('Annual Billing: {0}',
				[format_currency(info.billing_this_year, info.currency)]), 'blue')
			frm.dashboard_info.add_indicator(__('Last Year Billing: {0}',
				[format_currency(info.billing_last_year, info.currency)]), 'blue')
			frm.add_indicator(__('Total Unpaid: {0}',
				[format_currency(info.total_unpaid, info.currency)]),
				info.total_unpaid ? 'orange': 'green');
		}
	}
});
