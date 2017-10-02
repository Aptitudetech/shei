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

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    'Customer': {
        'validate': [
            'shei.events.on_customer_validate'
        ],
        'after_insert': [
            'shei.events.on_customer_after_insert'
        ]
    },
    'Sales Invoice': {
        'on_submit': [
            'shei.events.on_sales_invoice_onsubmit'
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
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "shei.event.get_events"
# }

