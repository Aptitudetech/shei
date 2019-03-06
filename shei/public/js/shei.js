/*
frappe.templates["dashboard_link_doctype"] = ' \
<div class="document-link" data-doctype="{{ doctype }}"> \
<a class="badge-link small">{{ __(doctype) }}</a> \
<span class="text-muted small count"></span> \
<span class="open-notification hidden" title="{{ __("Open {0}", [__(doctype)])}}"></span> \
	<button class="btn btn-new btn-default btn-xs hidden" data-doctype="{{ doctype }}"> \
			<i class="octicon octicon-plus" style="font-size: 12px;"></i> \
	</button>\
</div>';

frappe.provide('shei');


shei.dashboard_link_doctype = function(frm, doctype, section, links){
	var parent = $(format('.form-dashboard-wrapper h6:contains("{}")', [section])).parent();
	parent.find(format('div.document-link[data-doctype="{}"]', [doctype])).remove();
	parent.append(frappe.render_template('dashboard_link_doctype', {'doctype': doctype}));
	var self = parent.find(format('div.document-link[data-doctype="{}"]', [doctype]));
	shei.set_open_count(frm, doctype, links);
	// bind links
	self.find('.badge-link').on('click', function(){
		var routes = {};
		routes[frappe.scrub(frm.doc.doctype)] = frm.doc.name;
		frappe.route_options = routes;
		frappe.set_route('List', doctype);
	});

	// bind open notifications
	self.find('.open-notification').on('click', function() {
		frappe.route_options = {
			'quotation': frm.doc.name,
			'status': 'Draft'
		};
		frappe.set_route('List', doctype);
	});

	// bind new
	if (frappe.model.can_create(doctype)) {
		self.find('.btn-new').removeClass('hidden');

		self.find('.btn-new').on('click', function(){
			frappe.new_doc(doctype, {
				'project': frm.doc.name,
				'quotation_to': 'Customer',
				'customer': frm.doc.customer
			});
		});
	}
}

shei.set_open_count = function(frm, doctype, links){
	frappe.call({
		'method': 'shei.api.get_open_count',
		'args': {
			'doctype': frm.doctype,
			'name': frm.docname,
			'links': links
		},
		'callback': function(res){
			// update badges
			if (res && res.message){
				res.message.count.forEach(function(d){
					frm.dashboard.set_badge_count(
						d.name, cint(d.open_count), cint(d.count)
					);
				});
			}
		}
	});
}

frappe.ui.form.on('Project', 'refresh', function(frm, cdt, cdn){
	if (!frm.doc.__islocal){
		playworld.dashboard_link_doctype(frm, 'Quotation', __('Sales'), {
			'fieldname': 'project',
			'transactions': [
				{
					'items': ['Quotation'],
					'label': __('Quotation')
				}]
		});
	}
})*/










erpnext.accounts.SalesInvoiceController = erpnext.accounts.SalesInvoiceController.extend({
	"get_credit_notes": function(frm){
	if (frm.doc.customer){
		return frm.call({
			"method": "shei.events.get_credit_notes",
			"args": {
				"doctype": frm.doctype,
				"party_type": "customer",
				"party_name": frm.doc.customer
			},
			"callback": function(res){
				if (res && res.message){
					frm.clear_table('credits');
					var pending_amount = frm.doc.outstanding_amount, credits = 0.0;
					res.message.forEach(function(row){
						var d = frm.add_child('credits', row);
						if (d.allocated_amount > pending_amount){
							frappe.model.set_value(d.doctype, d.name,
								'allocated_amount', pending_amount);
						}
						pending_amount - d.allocated_amount;
						credits += d.allocated_amount;
					});
					frm.refresh_field("credits");
					frm.set_value("total_credits", credits);
				}
			}
		});
	}
	}
});


$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));

$.extend(erpnext.utils, {
	set_party_dashboard_indicators: function(frm){
		if (frm.doc.__onload && frm.doc.__onload.dashboard_info){
			var info = frm.doc.__onload.dashboard_info;
			frm.dashboard_info.add_indicator(__('Annual Billing: {0}',
				[format_currency(info.billing_this_year, info.currency)]), 'blue')
			frm.dashboard_info.add_indicator(__('Last Year Billing: {0}',
				[format_currency(info.billing_last_year, info.currency)]), 'blue')
			frm.add_indicator(__('Total Unpaid: {0}',
				[format_currency(info.total_unpaid, info.currency)]),
				info.total_unpaid ? 'orange': 'green');
		}
	}
});

/*
frappe.ui.form.on('Quotation', 'refresh', function(frm, cdt, cdn){
	if (!frm.doc.__islocal){
		shei.dashboard_link_doctype(frm, 'Product Configurator', __('Sales Order'), {  //sales order = where the link should be displayed
			'fieldname': 'quote',
			'transactions': [
				{
					'items': ['Product Configurator'],
					'label': __('Product Configurator')
				}]
		});
	}
});

shei.dashboard_link_doctype = function(frm, doctype, section, links){
	debugger;
	var parent = $(format('.form-dashboard-wrapper h6:contains("{}")', [section])).parent();
	parent.find(format('div.document-link[data-doctype="{}"]', [doctype])).remove();
	parent.append(frappe.render_template('dashboard_link_doctype', {'doctype': doctype}));
	var self = parent.find(format('div.document-link[data-doctype="{}"]', [doctype]));
	shei.set_open_count(frm, doctype, links);
	// bind links
	self.find('.badge-link').on('click', function(){
		var routes = {};
		routes[frappe.scrub(frm.doc.doctype)] = frm.doc.name;
		frappe.route_options = routes;
		frappe.set_route('List', doctype);
	});

	// bind open notifications
	self.find('.open-notification').on('click', function() {
		frappe.route_options = {
			'product_configurator': frm.doc.name//,
			//'status': 'Draft'
		};
		frappe.set_route('List', doctype);
	});
}

shei.set_open_count = function(frm, doctype, links){
	frappe.call({
		'method': 'shei.api.get_open_count',
		'args': {
			'doctype': frm.doctype,
			'name': frm.docname,
			'links': links
		},
		'callback': function(res){
			// update badges
			if (res && res.message){
				res.message.count.forEach(function(d){
					frm.dashboard.set_badge_count(
						d.name, cint(d.open_count), cint(d.count)
					);
				});
			}
		}
	});
}

*/