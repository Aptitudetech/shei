// Copyright (c) 2016, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Advance Payment', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Advance Payment", "refresh", function(frm) {
	if(frm.doc.docstatus == 0){
        	frm.add_custom_button(__("Import advance payment for client"), function() {
            	
		// When this button is clicked, do this
                frm.call({
                        'method': 'import_advance_payment',
                        'doc': frm.doc,
                        'args': {},

                        callback: function() {
                                frm.refresh()
                        }
                });
            });
        }
});

frappe.ui.form.on("Advance Payment", "project", function(frm, cdt, cdn) {
	frappe.call({
		method: "shei.advance_payment.get_customer_from_project",
		args:{
			project: frm.doc.project,
		},
        	callback: function(r) {
			frappe.model.set_value(cdt, cdn, "customer", r.message);
        	}
	});
});

//project name
//--------------------------
cur_frm.fields_dict['project'].get_query = function(doc, cdt, cdn) {
	return{
		query: "erpnext.controllers.queries.get_project_name",
		filters: {'customer': doc.customer}
	}
}
