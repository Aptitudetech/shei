// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('States per Country', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on("States per Country", "refresh", function(frm, cdt, cdn) {
	if (frm.doc.__islocal){
		setTimeout(function(){
		frappe.model.set_value(cdt, cdn, "country", "");
	}, 1000);
	}
});
