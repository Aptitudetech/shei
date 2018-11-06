// Copyright (c) 2017, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit', {
        get_customer_deposit: function(frm) {
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
});

frappe.ui.form.on("Customer Deposit", "refresh", function(frm) {
    if(frm.doc.docstatus == 1 && frm.doc.final_invoice_date != null){
        frm.add_custom_button(__("Apply Customer Deposit"), function() {
            // When this button is clicked, do this
                frm.call({
                        'method': 'apply_customer_deposit',
                        'doc': frm.doc,
                        'args': {},
                        callback: function() {
                                cur_frm.reload_doc();
                        }
                });
            });
        }
//        frm.add_custom_button(__("Update Posting Date"), function() {
//                frappe.call({
//                        method: "update_posting_date",
//                        'doc': frm.doc,
//                        args: {
//                        },
//                        callback: function(r) {
//                        }
//                });
//        });
    });

frappe.ui.form.on("Customer Deposit", "project", function(frm, cdt, cdn) {
        if (!frm.doc.project) return;
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

