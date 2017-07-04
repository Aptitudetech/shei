# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
        
	columns = [_("Supplier") + ":Link/Supplier:240", _("Project") + ":Link/Project:240",
                _("Material Request Item") + ":Link/Item:240", _("Order Qte") + "::50", _("Completed Qty") + "::50", 
		_("Qty Left to Order") + "::50"]
        conditions = ""
        if filters.get("supplier"):
                conditions += " and s.name = %(supplier)s"
	if filters.get("project"):
                conditions += " and mr.project = %(project)s"

	data = get_data(conditions, filters)
        nb_row = len(data)
        x = 0
        #total_payment_amount = total_invoice = 0.00

        while x < nb_row:
		data[x][5] = float(data[x][3]) - float(data[x][4])
		x += 1

        #data.insert(int(x),["", "Total", round(total_invoice, 2), round(total_payment_amount, 2)])

	return columns, data

def get_data(conditions, filters):
        time_sheet = frappe.db.sql(""" SELECT s.name, mr.project, i.item_code, mri.qty, mri.ordered_qty, 0
                FROM `tabMaterial Request` mr
                LEFT JOIN `tabMaterial Request Item` mri ON  mr.name = mri.parent
                LEFT JOIN `tabItem` i ON mri.item_code = i.item_code
		LEFT JOIN `tabSupplier` s ON i.default_supplier = s.name
                WHERE mri.qty > mri.ordered_qty and mr.status = 'Submitted' %s order by s.name """%(conditions), filters, as_list=1)

        return time_sheet

