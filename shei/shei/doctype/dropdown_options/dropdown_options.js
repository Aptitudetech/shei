// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dropdown Options', {
	refresh: function(frm) {
		//console.log(frappe.meta.has_field('Price Configurator Item', 'back'));
	}
});

frappe.ui.form.on('Dropdown Options', {
    doctype_type: function(frm, cdt, cdn){
        var d = locals[cdt][cdn];
        if (!d.doctype_type) return;
		frappe.call({
				method: "get_valid_variable_name",
				doc: frm.doc,
				args: {
				},
			callback: function(res) {
				cur_frm.set_df_property("variable_name", "options", res['message']);
			}
		});
    }
});