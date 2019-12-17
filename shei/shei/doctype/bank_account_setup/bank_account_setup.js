// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Account Setup', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Deposit and Bank Account based on Currency', {
    currency: function(frm, cdt, cdn){
        let d = locals[cdt][cdn];
        if (!d.currency) return;
		if(d.currency !== frappe.defaults.get_default("currency")){
			frappe.model.set_value(cdt, cdn, 'multi_currency', 1);
			//d.toggle_reqd("gain_lost_account", true);
			//cur_frm.fields_dict.deposit_bank_account_list.grid.toggle_reqd("gain_lost_account", true);
		}
		else{
			frappe.model.set_value(cdt, cdn, 'multi_currency', 0);
			//d.toggle_reqd("gain_lost_account", false);
			//cur_frm.fields_dict.deposit_bank_account_list.grid.toggle_reqd("gain_lost_account", false);
		}
    }
});