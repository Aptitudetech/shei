// Copyright (c) 2017, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit Reception', {
	get_customer_deposit: function(frm) {
//		frappe.msgprint("test")
		frappe.call({
			method: "get_customer_deposit_quotation",
			doc: frm.doc,
			args: {
		},
		callback: function() {
			frm.refresh()
			}
		});
	},
        create_je: function(frm) {
//              frappe.msgprint("test")
                frappe.call({
                        method: "create_je",
                        doc: frm.doc,
                        args: {
                },
                callback: function() {
                        frm.refresh()
                        }
                });
        }

});

frappe.ui.form.on("Customer Deposit Reception", "project", function(frm, cdt, cdn) {
        frappe.call({
                method: "shei.sheipy.get_customer_from_project",
                args:{
                        project: frm.doc.project,
                },
                callback: function(r) {
                        frappe.model.set_value(cdt, cdn, "customer", r.message);
                }
        });
});

cur_frm.fields_dict['project'].get_query = function(doc, cdt, cdn) {
        return{
                query: "erpnext.controllers.queries.get_project_name",
                filters: {'customer': doc.customer}
        }
}

