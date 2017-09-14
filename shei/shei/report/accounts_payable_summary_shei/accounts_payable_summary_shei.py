# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from shei.shei.reports.accounts_receivable_summary_shei.accounts_receivable_summary_shei \
	import AccountsReceivableSummary

def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buy Settings", "supp_master_name"]
	}
	return AccountsReceivableSummary(filters).run(args)