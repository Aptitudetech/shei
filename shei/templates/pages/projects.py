# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
import datetime as dt

@frappe.whitelist()
def upload_wetransfer_link(doc_name, link):
	from frappe.email.doctype.email_template.email_template import get_email_template
	recipient = frappe.get_value('Project', doc_name, 'project_manager')
	#recipient =  frappe.get_value('User', project_manager, 'email')
	recipient = 'melissaraymond48@gmail.com'
	content = '<p>Hi,</p><p>You received some files from <a href="https://en-dev.shei.sh/desk#Form/Project/{0}".format(doc_name) target="_blank">{0}</a></p><p>To see them, please click on this link: <a href="{1}".format(link) target="_blank">WeTransfer</a></p>'.format(doc_name, link)
	frappe.sendmail(
		recipients=[recipient],
		#sender="xyz@gmail.com",
		subject="Files Received for project {0}".format(doc_name), 
		content=content
	)

@frappe.whitelist()
def update_shipping_address(doc_name, customer, address_title, address_line_1, address_city, address_country):
	if frappe.db.exists('Address', address_title+"-Shipping"):
		frappe.throw("Sorry, this address title already exist. Please choose something else")
	address = frappe.new_doc('Address')
	address.update({
		"address_title": address_title,
		"address_line1": address_line_1,
		"city": address_city,
		"country": address_country,
		"address_type": 'Shipping',
		"links": [{
			'link_doctype': 'Customer',
			'link_name': customer,
		}],
	})
	address.flags.ignore_permissions = True
	address.save()
	frappe.msgprint(_("name: {0}").format( address.name ))
	###send email



#SELECT
#  tabProject.name as "Project:Link/Project:250",
#  tabProject.shei_project_name as "Project Name:text:150",
#  tabProject.project_amount_from_so as "Amount:Currency:90",
#  tabProject.sub_type as "SubType:text:105",
#  tabTask.subject as "Subject:text:250",
#  tabTask.name as "Task:Link/Task:100",
#  tabTask.status as "Status:text:105",
#  tabProject.expected_end_date as "Exp. End Date:date:90",
#  tabProject.project_manager as "Project Manager:Link/User:150",
#  tabProject.type as "Type:text:105",
#  tabTask.assigned_to as "Assigned To:Link/User:150"
#FROM tabProject
#  LEFT OUTER JOIN tabTask
#    ON tabProject.name = tabTask.project
#WHERE tabTask.status <> 'Closed'
#AND tabProject.status = 'Open'
#OR tabProject.status = 'Project Without Orders'
#GROUP BY tabProject.name
#