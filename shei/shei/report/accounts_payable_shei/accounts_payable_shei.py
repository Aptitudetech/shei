# Copyright (c) 2013, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from shei.shei.report.accounts_receivable_shei.accounts_receivable_shei import ReceivablePayableReport

def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"]
	}

	return ReceivablePayableReport(filters).run(args)