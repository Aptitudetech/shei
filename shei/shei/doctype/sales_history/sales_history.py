# -*- coding: utf-8 -*-
# Copyright (c) 2015, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesHistory(Document):
	def test(self):
		for je in frappe.db.get_all("Journal Entry"):
                        je = frappe.get_doc("Journal Entry", je.name)
			if 'JV-IMPORT-AP-' in je.name:
				je.cancel()
				je.delete()
