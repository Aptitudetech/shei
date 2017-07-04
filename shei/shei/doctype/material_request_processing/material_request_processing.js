// Copyright (c) 2017, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Request Processing', {
        get_open_material_request_items: function(frm) {
                frappe.call({
                        method: "get_open_material_request_items",
                        doc: frm.doc,
                        args: {
                        },
                callback: function() {
                        frm.refresh()
                        }
                });
        },
        create_purchase_order: function(frm) {
                frappe.call({
                        method: "create_purchase_order",
                        doc: frm.doc,
                        args: {
                        },
                callback: function() {
//                        frm.refresh()
                        }
                });
        },
        sort_default_supplier: function(frm) {
                frappe.call({
                        method: "sort_default_supplier",
                        doc: frm.doc,
                        args: {
				sort: "default_supplier"
                        },
                callback: function() {
                        frm.refresh()
                        }
                });
        },
        sort_po_supplier: function(frm) {
                frappe.call({
                        method: "sort_po_supplier",
                        doc: frm.doc,
                        args: {
				sort: "po_supplier"
                        },
                callback: function() {
                        frm.refresh()
                        }
                });
        },
        sort_required_date: function(frm) {
                frappe.call({
                        method: "sort_required_date",
                        doc: frm.doc,
                        args: {
				sort: "required_date"
                        },
                callback: function() {
                        frm.refresh()
                        }
                });
        },
});

frappe.ui.form.on("Material Request Processing", "refresh", function(frm) {
	frm.disable_save();
});
