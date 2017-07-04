# -*- coding: utf-8 -*-
# Copyright (c) 2017, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MaterialRequestProcessing(Document):

        def get_open_material_request_items(self):
                self.material_request_processing_item = []
		if self.project:
			strFilter = {"material_request_type": "Purchase", "project": self.project, "status": "Submitted", "per_ordered": ("<", 100), "docstatus": 1}
		else:
			strFilter = {"material_request_type": "Purchase", "status": "Submitted", "per_ordered": ("<", 100), "docstatus": 1}

                for i in frappe.get_list("Material Request", fields="name", filters=strFilter):
			mr = frappe.get_doc("Material Request", i.name)
			for i in mr.get('items'):
				if i.ordered_qty < i.qty:
					ds = ""
					ds = frappe.get_value("Item", i.item_code, "default_supplier")
                	        	self.append("material_request_processing_item", {
                        	        	"default_supplier": ds,
						"po_supplier": ds,
                                		"item_code": i.item_code,
                                		"supplier_quotation": i.supplier_quotation,
						"quantity_to_order": i.qty - i.ordered_qty,
						"required_date": i.schedule_date,
						"warehouse": i.warehouse,
						"material_request": mr.name
                        		})
		for i, item in enumerate(sorted(self.material_request_processing_item, key=lambda item: item.default_supplier), start=1):
			item.idx = i

#        def create_purchase_order(self):
#		if self.material_request_processing_item:
#				
#
#			for i in self.material_request_processing_item:
#			for i
#
#                        po = frappe.new_doc("Purchase Order")
#                        json_update = {
#                                "naming_series": "PO-",
#			}









				

	def sort_default_supplier(self, sort):
		if self.material_request_processing_item:
	                for i, item in enumerate(sorted(self.material_request_processing_item, key=lambda item: item.default_supplier), start=1):
        	                item.idx = i
		else:
			frappe.msgprint("Nothing to sort")

        def sort_po_supplier(self):
                if self.material_request_processing_item:
	                for i, item in enumerate(sorted(self.material_request_processing_item, key=lambda item: item.po_supplier), start=1):
        	                item.idx = i
                else:
                        frappe.msgprint("Nothing to sort")

        def sort_required_date(self):
                if self.material_request_processing_item:
        	        for i, item in enumerate(sorted(self.material_request_processing_item, key=lambda item: item.required_date), start=1):
                	        item.idx = i
                else:
                        frappe.msgprint("Nothing to sort")
