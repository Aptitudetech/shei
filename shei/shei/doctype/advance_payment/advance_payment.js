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
