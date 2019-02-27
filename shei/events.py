#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import types
import json
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, add_to_date, flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext import get_default_currency
from erpnext.accounts.party import (get_party_account_currency)

def get_dashboard_info(party_type, party):
	current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
	company = frappe.db.get_default("company") or frappe.get_all("Company")[0].name
	party_account_currency = get_party_account_currency(party_type, party, company)
	company_default_currency = get_default_currency() \
		or frappe.db.get_value('Company', company, 'default_currency')

	if party_account_currency == company_default_currency:
		total_field = "base_grand_total"
	else:
		total_field = "grand_total"

	doctype = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"

	info = {}
	for i, dates in enumerate(((current_fiscal_year.year_start_date, current_fiscal_year.year_end_date),
		      (add_to_date(current_fiscal_year.year_start_date, years=-1), 
		       add_to_date(current_fiscal_year.year_end_date, years=-1)))):
		billing = frappe.db.sql("""
		select sum({0})
		from `tab{1}`
		where {2}=%s and docstatus=1 and posting_date between %s and %s
		""".format(total_field, doctype, party_type.lower()), 
			(party, dates[0], dates[1]))

		if i == 0:
			info['billing_this_year'] = flt(billing[0][0]) if billing else 0
		else:
			info['billing_last_year'] = flt(billing[0][0]) if billing else 0

	total_unpaid = frappe.db.sql("""
		select sum(debit_in_account_currency) - sum(credit_in_account_currency)
		from `tabGL Entry`
		where party_type = %s and party=%s""", (party_type, party))
	
	info['currency'] = party_account_currency
	info['total_unpaid'] = flt(total_unpaid[0][0]) if total_unpaid else 0
	if party_type == "Supplier":
		info["total_unpaid"] = -1 * info["total_unpaid"]

	return info

def on_party_onload(doc, handler):
    doc.set_onload("dashboard_info", get_dashboard_info(doc.doctype, doc.name))


def on_customer_validate(doc, handler=None):
#    if doc.is_new() and not doc.lead_name:
#        frappe.throw('Sorry, you need to create a Lead first')
    if not doc.get('customer_code'):
        doc.customer_code = frappe.db.get_value(
            'Custom Series',
            {'name': 'Customer'},
            'series'
        )


def on_customer_after_insert( doc, handler=None ):
    if doc.customer_code:
        frappe.db.set_value(
            'Custom Series',
            {'name': 'Customer'},
            'series',
            doc.customer_code + 1
        )


@frappe.whitelist()
def get_credit_notes( doctype, party_type, party_name ):
    sql = """
    SELECT '{0}' as `reference_type`,
        `tab{0}`.name as `reference_name`,
        `tab{0}`.remarks as `remarks`,
        abs(`tab{0}`.outstanding_amount) as `credit_amount`,
        abs(`tab{0}`.outstanding_amount) as `allocated_amount`
    FROM `tab{0}`
    WHERE `tab{0}`.outstanding_amount < 0
        AND `tab{0}`.`{1}` = %s
    GROUP BY `tab{0}`.`name`
    """.format(doctype, party_type)
    return frappe.db.sql(sql, (party_name,), as_dict=True)


def on_sales_invoice_submit( doc, handler=None ):
    if doc.get("credits"):
        je = frappe.new_doc('Journal Entry').update({
            "voucher_type": "Journal Entry",
            "posting_date": doc.posting_date,
            "company": doc.company,
            "multi_currency": doc.currency != frappe.db.get_value("Company", doc.company, "default_currency")
        })
        d_or_c = doc.debit_to if doc.doctype == "Sales Invoice" else doc.credit_to
        party = "Customer" if doc.doctype == "Sales Invoice" else "Supplier"

        doc.total_credits = 0.0
        for row in doc.credits:
            doc.total_credits += row.allocated_amount
            je.append("accounts",{
                "account": d_or_c,
                "party_type": party,
                "party": doc.get( frappe.scrub(party) ),
                "debit_in_account_currency": row.allocated_amount,
		"exchange_rate": doc.conversion_rate,
                "reference_type": row.reference_type,
                "reference_name": row.reference_name
            })
        je.append("accounts", {
            "account": d_or_c,
            "party_type": party,
            "party": doc.get( frappe.scrub(party) ),
            "credit_in_account_currency": row.allocated_amount,
            "exchange_rate": doc.conversion_rate,
            "reference_type": doc.doctype,
            "reference_name": doc.name
        })
        try:
            je.run_method('validate')
        except:
            frappe.clear_messages()
	if je.accounts[0].debit != je.accounts[1].credit:
		debit = je.accounts[0].debit
		credit = je.accounts[1].credit
		je.append("accounts", {
			"account": frappe.db.get_value("Company", doc.company, "exchange_gain_loss_account"),
			"credit_in_account_currency": debit - credit if credit < debit else 0.0,
			"debit_in_account_currency": credit - debit if debit < credit else 0.0
		})
        je.save()
        je.submit()
        doc.db_set('debit_note', je.name, update_modified=False)


def before_sales_invoice_cancel( doc, handler=None ):
    if doc.get("debit_note"):
        je = frappe.get_doc("Journal Entry", doc.debit_note)
        je.flags.ignore_links = True
        je.cancel()

def on_sales_invoice_validate(doc, handler=None):
    if doc.is_new():
        has_delivery_note = any([item.delivery_note for item in doc.items])
        if not has_delivery_note and frappe.db.exists("SHEI_Settings", "SHEI_Settings"):
            settings = frappe.get_doc("SHEI_Settings", "SHEI_Settings")

            user_restriction = settings.get("restrictions",{
                "source_doctype": "Sales Order",
                "user": frappe.session.user
            })
            if user_restriction:
                frappe.throw("You're not allowed to create invoices from here !") 
