
frappe.ui.form.on("Sales Invoice", "get_credit_notes", function(frm, cdt, cdn){
	frappe.call({
		"method": "shei.events.get_credit_notes",
		"args": {
			"doctype": frm.doctype,
			"docname": frm.name
		},
		"callback": function(res){
			if(res && res.message){
				frm.clear_table("credits");
				res.message.forEach(function(row){
					var d = frm.add_child('credits', row)
				});
				frm.refresh_field('credits');
			}
		}
	});
});