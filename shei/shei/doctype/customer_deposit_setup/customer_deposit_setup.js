// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit Setup', {
	refresh: function(frm) {
	}
});

frappe.ui.form.on('Deposit and Bank Account based on Currency', {
    currency: function(frm, cdt, cdn){
        let d = locals[cdt][cdn];
        if (!d.currency) return;
        console.log(d.currency);
        console.log(frappe.defaults.get_default("currency"));
        console.log(d.currency != frappe.defaults.get_default("currency"));
		if(d.currency != frappe.defaults.get_default("currency")){
			frappe.model.set_value(cdt, cdn, 'multi_currency', 1);
			cur_frm.fields_dict.child_table_name.grid.toggle_reqd("child_table_fieldname", condition)
		}
		else{
			frappe.model.set_value(cdt, cdn, 'multi_currency', 0);
			cur_frm.fields_dict.child_table_name.grid.toggle_reqd("child_table_fieldname", condition)
		}
    }
});
