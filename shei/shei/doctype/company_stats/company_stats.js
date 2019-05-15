// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Stats', {
	refresh: function(frm) {
		frm.disable_save();
		console.log("hey");
		console.log(cur_frm.doc.so_curr_month);

		var node = document.createElement("p");                 // Create a <li> node
		var textnode = document.createTextNode("some Text");         // Create a text node
		node.appendChild(textnode);                              // Append the text to <li>
		document.getElementById("so_today").appendChild(node);     // Append <li> to <ul> with id="myList"
	},
	after_rendering: function(frm){
	},
	btn_load_complete_report: function(frm) {
		frappe.call({
				method: "load_complete_report",
				doc: frm.doc,
				args: {
				},
				freeze: true,
					freeze_message: "This operation may takes few minutes, please wait...",
			callback: function() {
				refresh_field("sales_order_today_table");
				refresh_field("sales_order_curr_month");
				refresh_field("oo_table_today");
				refresh_field("oo_table_curr_month");
				refresh_field("quote_table_today");
				refresh_field("quote_table_month");
				refresh_field("quote_table_one_year_old");
			}
		});
	},
	btn_load_resume_button: function(frm) {
		frappe.call({
				method: "btn_load_resume_button",
				doc: frm.doc,
				args: {
				},
				freeze: true,
					freeze_message: "This operation may takes few minutes, please wait...",
			callback: function() {
				refresh_field("sales_order_today_table");
				refresh_field("sales_order_curr_month");
				refresh_field("oo_table_today");
				refresh_field("oo_table_curr_month");
				refresh_field("quote_table_today");
				refresh_field("quote_table_month");
				refresh_field("quote_table_one_year_old");
			}
		});
	},
});

