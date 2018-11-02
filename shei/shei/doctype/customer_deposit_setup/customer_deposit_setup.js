// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit Setup', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Customer Deposit Setup', 'onload_post_render', function(frm){
    frm.set_query('deposit_account', 'deposit_setting', function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		console.log("OK")
		console.log(d);
        if (!d.deposit_currency) return;
        return {
           'filters': {
               "deposit_currency": d.deposit_currency
           }
       }
    })
});

//DONT FILTER AND NEED TO DO BEFORE_SAVE ON CHILD TABLE TO SET MULTI CURRENCY