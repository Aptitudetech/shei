#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import types
import json
from frappe.model.naming import make_autoname


def on_customer_validate(doc, handler=None):
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
    """.format(doctype, party_type)
    return frappe.db.sql(sql, (party_name,), as_dict=True)


def on_sales_invoice_submit( doc, handler=None ):
    if doc.get("credits"):
        je = frappe.new_doc('Journal Entry').update({
            "voucher_type": "Journal Entry",
            "posting_date": doc.posting_date,
            "company": doc.company
        })
        d_or_c = doc.debit_to if doc.doctype == "Sales Invoice" else doc.credit_to
        party = "Customer" if doc.doctype == "Sales Invoice" else "Supplier"

        for row in doc.credits:
            je.append("accounts",{
                "account": d_or_c,
                "party_type": party,
                "party": doc.get( frappe.scrub(party) ),
                "debit_in_account_currency": row.allocated_amount,
                "reference_type": doc.doctype,
                "reference_name": doc.name
            })
            je.append("accounts", {
                "account": d_or_c,
                "party_type": party,
                "party": doc.get( frappe.scrub(party) ),
                "debit_in_account_currency": row.allocated_amount,
                "reference_type": doc.doctype,
                "reference_name": doc.name
            })
        je.save()
        je.submit()