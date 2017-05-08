// Copyright (c) 2016, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales History', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Sales History", "refresh", function(frm) {
        frm.add_custom_button(__("Effacer mauvaise trans"), function() {
            // When this button is clicked, do this
                frm.call({
                        'method': 'test',
                        'doc': frm.doc,
                        'args': {},

                        callback: function() {
                                cur_frm.refresh();
                        }
                });
            });
    });
