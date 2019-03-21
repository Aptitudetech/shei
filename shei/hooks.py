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
    'Project': {
        'validate_dates': [
            'shei.events.on_project_validate_dates'
        ]
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
#override_whitelisted_methods = {
#    "frappe.core.doctype.communication.email.make": "shei.events.make",
#    #"frappe.desk.doctype.event.event.get_events": "shei.event.get_events",
#    "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": "shei.route.make_sales_invoice",
# 	"frappe.model.mapper.make_mapped_doc": "shei.route.make_mapped_doc",
#    "frappe.model.mapper.map_docs": "shei.route.map_docs"
#}

fixtures = [
    {'dt': 'Print Node Settings'},
    {
        "dt": "Custom Field",
	    "filters": {
        	"name": ["in", [
			    "Sales Order-work_order",
                "Sales Order-create_work_order",
                "Item-price_per_sqft",
                "Issue-kanban_status",
                "Lead-others",
                "Lead-specify",
                "Lead-lead_qualification",
                "Lead-company_size",
                "Lead-lead_last_name",
                "Quotation-create_price_configurator",
                "Quotation-price_configurator",
                "Bank Account-is_deposit_account",
                "Bank Account-deposit_account",
                "Bank Account-currency",
         	]]
    	}
    },
    { 
        "dt": "Custom Script", 
        "filters": { 
            "name": ["in", [ 
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
