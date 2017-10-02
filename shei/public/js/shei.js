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
					res.message.forEach(function(row){
						var d = frm.add_child('credits', row);
					});
					frm.refresh_field("credits");
				}
			}
		});
	}
	}
});

$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));