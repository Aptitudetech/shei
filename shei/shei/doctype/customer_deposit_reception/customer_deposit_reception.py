# -*- coding: utf-8 -*-
# Copyright (c) 2017, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document
from frappe import _


class CustomerDepositReception(Document):

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            je.cancel()
            je.delete()
            frappe.db.set_value("Customer Deposit Reception", self.name, "journal_entry", "")
        for i in self.get('customer_deposit_quotation'):
            frappe.db.set_value("Quotation", i.quotation, "customer_deposit_received", False)

    def get_customer_deposit_quotation(self):
        self.customer_deposit_quotation = []
        for qt in frappe.get_list("Quotation", fields=["name", "total", "grand_total", "status"],
                                  filters={"customer_deposit": True, "customer_deposit_received": False,
                                           "docstatus": 1, "customer": self.customer}):
            self.append("customer_deposit_quotation", {
                "quotation": qt.name,
                "total_before_taxes": qt.total,
                "grand_total": qt.grand_total
            })

    def on_submit(self):
        customer_deposit_setup = frappe.db.get_value('Customer Deposit Setup', 'Customer Deposit Setup',
                                                     ['*'], as_dict=True)
        customer_currency = frappe.db.get_value("Customer", {'customer_name': self.customer}, "default_currency")
        bank_deposit_currency = frappe.db.get_value('Deposit and Bank Account based on Currency',
                                                    {'currency': customer_currency}, '*', as_dict=True)
        if not bank_deposit_currency:
            frappe.msgprint(
                "The currency of customer " + self.customer + " is not supported by this module at this time.")
            exit()
        je = frappe.new_doc("Journal Entry")
        json_update = {
            "naming_series": "CD-",
            "voucher_type": "Cash Entry",
            "posting_date": self.posting_date,
            "company": frappe.db.get_default("company"),
            "multi_currency": bank_deposit_currency['multi_currency'],
            "remark": "Deposit",
            "write_off_based_on": "Accounts Receivable",
            "write_off_amount": 0,
            "pay_to_recd_from": self.customer,
            "letter_head": "Standard - header & footer",
            "is_opening": "No",
        }
        je.update(json_update)

        # On passe toutes les soumissions pour appliquer les taxes (si <> USD) et totaux envers le compte Avances Client
        ref = ""
        for i in self.get('customer_deposit_quotation'):
            qt = frappe.get_doc("Quotation", i.quotation)
            frappe.db.set_value("Quotation", i.quotation, "customer_deposit_received", True)
            if ref:
                ref = ref + ", " + qt.name
            else:
                ref = qt.name

            je.append("accounts", {
                "account": bank_deposit_currency['deposit_account'],
                "balance": 0,
                "cost_center": customer_deposit_setup['default_cost_center'],
                "party_type": "Customer",
                "party": self.customer,
                "party_balance": 0,
                "account_currency": qt.currency,
                "exchange_rate": qt.conversion_rate,
                "debit_in_account_currency": 0,
                "debit": 0,
                "credit_in_account_currency": qt.grand_total,
                "credit": qt.base_grand_total,
                "project": self.project,
                "is_advance": "Yes"
            })
            je.append("accounts", {
                "account": bank_deposit_currency['bank_account'],
                "balance": 0,
                "cost_center": customer_deposit_setup['default_cost_center'],
                "account_currency": qt.currency,
                "exchange_rate": qt.conversion_rate,
                "debit_in_account_currency": qt.grand_total,
                "debit": qt.base_grand_total,
                "credit_in_account_currency": 0,
                "credit": 0,
                "project": self.project,
            })

            # On crédite les taxes dans les comptes de taxes et on débite dans le compte de taxes temporaire
            for t in qt.get('taxes'):
                je.append("accounts", {
                    "account": t.account_head,
                    "balance": 0,
                    "cost_center": customer_deposit_setup['default_cost_center'],
                    "account_currency": qt.currency,
                    "exchange_rate": qt.conversion_rate,
                    "debit_in_account_currency": 0,
                    "debit": 0,
                    "credit_in_account_currency": t.tax_amount,
                    "credit": t.base_tax_amount,
                    "project": self.project,
                    "is_advance": "No"

                })
                je.append("accounts", {
                    "account": customer_deposit_setup['account_for_sales_tax'],
                    "balance": 0,
                    "cost_center": customer_deposit_setup['default_cost_center'],
                    "account_currency": qt.currency,
                    "exchange_rate": qt.conversion_rate,
                    "debit_in_account_currency": t.tax_amount,
                    "debit": t.base_tax_amount,
                    "credit_in_account_currency": 0,
                    "credit": 0,
                    "project": self.project,
                    "is_advance": "No"
                })
        json_update = {
            "user_remark": "Applying customer deposit (Ref.: " + ref + ") to Avance Client receivable account",
        }
        je.update(json_update)
        je.save()
        frappe.db.set_value("Customer Deposit Reception", self.name, "journal_entry", je.name)
        je.submit()
