// Copyright (c) 2018, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit Setup', {
	refresh: function(frm) {
        frm.set_query('receivable_account', 'deposit_setting', function(doc, cdt, cdn){
            var d = locals[cdt][cdn];
            if (!d.account_currency) return;
            var ret = {};
            frappe.call({
                'method': 'shei.shei.doctype.customer_deposit_setup.customer_deposit_setup.get_receivable_account_by_currency',
                'args': {
                    'chosen_currency': d.account_currency
                },
                'callback': function(banks){
                        ret = banks.message;
                },
                'async': false // <-- This is important
            });
            return {
               'filters': {
                    "name": ["in", ret]
               }
           }
        })
	}
});