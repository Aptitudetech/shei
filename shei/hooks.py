# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "shei"
app_title = "SHEI"
app_publisher = "Aptitude technologie"
app_description = "Module for SHEI"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@aptitudetech.net"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/shei/css/shei.css"
app_include_js = "/assets/js/shei.js"

# include js, css files in header of web template
# web_include_css = "/assets/shei/css/shei.css"
# web_include_js = "/assets/shei/js/shei.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "shei.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "shei.install.before_install"
# after_install = "shei.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "shei.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways
permission_query_conditions = {
 	"Project": "shei.permissions.get_project_permissions_query_conditions",
}

#has_permission = {
# 	"Report": "shei.permissions.has_permission_to_report",
#}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    'Customer': {
        'onload': [
            'shei.events.on_party_onload'
        ],
        'validate': [
            'shei.events.on_customer_validate'
        ],
        'after_insert': [
            'shei.events.on_customer_after_insert'
        ]
    },
    'Issue': {
	'before_save': [
	    'shei.events.on_issue_before_save'
	],
    },
#    'Quotation': {
 #       'validate': [
  #          'shei.events.on_quotation_validate'
   #     ]
    #},
    'Project': {
	'onload': [
		'shei.events.on_project_onload'
	],
    },
    'Sales Invoice': {
        #'validate':[
        #    'shei.events.on_sales_invoice_validate'
        #],

        'on_submit': [
            'shei.events.on_sales_invoice_submit'
        ],
        'before_cancel': [
            'shei.events.before_sales_invoice_cancel'
        ]
    },
    'Supplier': {
        'onload': [
            'shei.events.on_party_onload'
        ]
    }
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"shei.tasks.all"
# 	],
# 	"daily": [
# 		"shei.tasks.daily"
# 	],
# 	"hourly": [
# 		"shei.tasks.hourly"
# 	],
# 	"weekly": [
# 		"shei.tasks.weekly"
# 	]
# 	"monthly": [
# 		"shei.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "shei.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.form.assign_to.add":"shei.route.assign_to_notify",
#    "frappe.core.doctype.communication.email.make": "shei.events.make",
#    #"frappe.desk.doctype.event.event.get_events": "shei.event.get_events",
#    "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": "shei.route.make_sales_invoice",
# 	"frappe.model.mapper.make_mapped_doc": "shei.route.make_mapped_doc",
#    "frappe.model.mapper.map_docs": "shei.route.map_docs"
}


fixtures = [
    {'dt': 'Print Node Settings'},
    {'dt': 'Website Settings'},
    {'dt': 'Portal Settings'},
    {
        "dt": "Property Setter",
        "filters": {
            "name": ["in", [
                "Project Task-title-options",
                "Task-subject-options",
                "Task-subject-fieldtype",
                "Project Task-title-fieldtype",
            ]]
        }
    },
    {
        "dt": "Custom Field",
	    "filters": {
        	"name": ["in", [
                "Address-have_dock",
                "Address-is_residential_address",
                "Project-absolute_end_date",
                "Project-restricted_to_role",
                "Project-shipping_informations",
                "Project-crates",
                "Item-hts_name",
                "Project-kanban_task_status",
                "Workstation Working Hour-saturday",
                "Workstation Working Hour-friday",
                "Workstation Working Hour-thursday",
                "Workstation Working Hour-wednesday",
                "Workstation Working Hour-tuesday",
                "Workstation Working Hour-monday",
                "Workstation Working Hour-sunday",
		"Employee-workstation",
		"Sales Order-work_order",
                "Item-price_per_sqft",
                "Issue-kanban_status",
                "Lead-others",
                "Lead-specify",
                "Lead-lead_qualification",
                "Lead-company_size",
                "Lead-lead_last_name",
                "Quotation-price_configurator",
                "Bank Account-is_deposit_account",
                "Bank Account-deposit_account",
                "Bank Account-currency",
                "Project-please_explain",
                "Project-satisfaction_level",
                "Project-client_satisfaction",
                "Material Request Item-required_from",
                "Journal Entry-deposit_ticket",
                "Payment Entry-deposit_ticket",
                "Project-advance_and_payment",
                "Project-project_manager",
                "Project-sales_person",
                "Deleted Document-gcalendar_sync_id",
                "Event-gcalendar_sync_id",
                "Sales Order Item-need_manufacture",
                "Sales Order Item-work_order_description",
                "Quotation-sales_status",
                "Quotation-potential_level",
                "Company-bank_information",
                "Customer-bank_information",
                "Supplier-bank_information",
                "Item-workflow_state",
                "BOM-workflow_state",
                "Sales Order-eft_file_accepted",
                "Sales Order-eft_generate_sales_invoice_after_confirm_file_acceptation",
                "Sales Order-eft_payment_request_on_submit",
                "Sales Order-eft_bank_account",
                "Customer-bank_details",
                "Supplier-bank_details",
                "Company-bank_details",
                "Deleted Document-github_sync_id",
                "Task-github_sync_id",
                "Project-github_sync_id",
                "Deleted Document-hub_sync_id",
                "Lead-hub_sync_id",
                "Item-hub_sync_id",
                "Print Settings-print_taxes_with_zero_amount",
                "Job Applicant-city",
                "Job Applicant-date_applied",
                "Job Applicant-department",
                "Quotation-other_version_existing_quote_sh_",
                "Sales Invoice-total_credits",
                "Sales Invoice-debit_note",
                "Sales Invoice-credits",
                "Sales Invoice-get_credit_notes",
                "Sales Invoice-credit_notes",
                "Account-overhead_accounts_shi",
                "Project-marketing_budget_sh",
                "Employee-status_sh",
                "Employee-extension",
                "Purchase Order Item-asked_by",
                "Issue-end_time__shei",
                "Issue-start_time_shei",
                "Project-project_contact",
                "Project-sb_project_contact",
                "Stock Entry-sales_order",
                "Employee-kanban_column",
                "Project-shei_project_name",
                "Project-contact",
                "Task-customer_approval",
                "Quotation Item-col_break",
                "Quotation Item-spec",
                "Project Task-assigned_to",
                "Task-assigned_to",
                "Project-customer_deposit_item",
                "Project-project_amount_from_so",
                "Project-kanban_column",
                "Material Request Item-supplier_quotation",
                "Quotation-project",
                "Customer Deposit-final_invoice_date",
                "Quotation-customer_deposit_received",
                "Quotation-customer_deposit",
                "Material Request-project",
                "Quotation-sales_person",
                "Quotation-reference",
                "Project-sub_type",
                "Project-type",
                "Accounts Settings-cheque_series",
                "Appraisal Goal-notes",
                "Sales Order Item-bom_no",
                "Sales Order Item-height_in_mm",
                "Sales Order Item-width_in_mm",
                "Quotation Item-bom_no",
                "Employee-hours_per_pay_period",
                "Item-item_description",
                "Sales Order Item-height_in_inches",
                "Sales Order Item-width_in_inches",
                "Quotation Item-height_in_mm",
                "Quotation Item-width_in_mm",
                "Quotation Item-height_in_inches",
                "Quotation Item-width_in_inches",
                "Journal Entry Account-note",
                "Employee-social_security_number",
                "Employee-current_wage_start_date",
                "Employee-hourly_wage",
                "Account-list_of_employees",
                "Item-temporary_quantity",
                "Item-location",
                "Item-detailed_description",
                "Print Settings-compact_item_print",
         	]]
    	}
    },
    {'dt': 'Web Page'},
    {
        "dt": "Print Format",
	    "filters": {
        	"name": ["in", [
                "shei - Bill Of Lading",
                "shei - Commercial Invoice",
			    "SHEI - SO Work Order",
                "shei - Cheque BNC",
                "shei - Packing Slip",
                "shei - Material Request",
                "shei - Payment Entry",
                "shei - Purchase Order",
                "shei - Work Order",
                "shei - Pro Format Invoice - Invoice",
                "shei - Pro Format Invoice",
                "shei - Quotation - Architectural",
                "shei - Sales Invoice",
                "shei - Sales Invoice - With Project Name SHEI",
                "shei - Sales Order",
                "shei - Quotation - Graphic",
                "shei - Delivery Note",
                "shei - Cheque BMO",
                "shei - Cheque BMO - JV",
                "shei - EFT",
                "shei - Item label",
         	]]
    	}
    },
    {
        "dt": "Custom Script",
        "filters": {
            "name": ["in", [
		"Delivery Note-Client",
                "Sales Order-Client",
                "Quotation-Client",
                "Bank Account-Client",
                "Supplier-Client",
                "Customer-Client",
                "Project-Client",
                "Sales Invoice-Client",
                "Terms and Conditions Multilingual Extension-Client",
                "Stock Entry-Client",
                "Purchase Invoice-Client",
                "Payment Entry-Client",
            ]]
        }
    },
]
