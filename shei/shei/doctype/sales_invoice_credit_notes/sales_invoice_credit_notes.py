# -*- coding: utf-8 -*-
# Copyright (c) 2017, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesInvoiceCreditNotes(Document):
	pass


@frappe.whitelist()
def get_credit_notes(party_type, party, company):
	if frappe.db.exists("Party Account", {
		"parent": party,
		"parent_type": party_type,
		"company": company
		}):
		party_account = frappe.db.get_value("Party Account", {
			"parent": party,
			"parent_type": party_type,
			"company": company
		}, "account")
	else:
		frappe.db.get_value("Company", company, "default_receivable_account")
	
	credit_notes = frappe.db.sql("""
		SELECT
			`tabJournal Entry Account`.`name` as 
	""")