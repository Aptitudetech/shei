# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
import datetime as dt

@frappe.whitelist()
def upload_wetransfer_link(doc_name, link):
	recipient = frappe.get_value('Project', doc_name, 'project_manager')
	recipient = 'melissaraymond48@gmail.com'
	content = _('<p>Hi,</p><p>You received some files from <a href="https://en-dev.shei.sh/desk#Form/Project/{0}".format(doc_name) target="_blank">{0}</a></p><p>To see them, please click on this link: <a href="{1}".format(link) target="_blank">WeTransfer</a></p>').format(doc_name, link)
	subject = "Files Received for project {0}".format(doc_name)
	send_email(recipient, subject, content)

@frappe.whitelist()
def update_address_information(address_list = []):
	for address in address_list:
		address = frappe.get_doc('Address', address['address_name']).update({'is_residential_address': address['is_residential'], 'have_dock': address['have_dock']})
		address.flags.ignore_permissions = True
		address.save()

@frappe.whitelist()
def send_email(recipient, subject, content):
	from frappe.email.doctype.email_template.email_template import get_email_template
	frappe.sendmail(
		recipients=[recipient],
		subject=subject, 
		content=content
	)

@frappe.whitelist()
def create_shipping_address(address_title, address_line_1, address_city, address_country, customer):
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
	return address

@frappe.whitelist()
def update_shipping_address(doc_name, sales_order_name, customer, address_line_1, address_city, address_country, address_title, checked_address_value, address_info_list = []):
	address_validation(address_title, address_line_1, address_city, address_country, checked_address_value)
	address_list = json.loads(address_info_list)
	update_address_information(address_list)
	if address_title:
		new_address = create_shipping_address(address_title, address_line_1, address_city, address_country, customer)
		shipping_address = new_address.name
	else:
		shipping_address = checked_address_value
	#send email
	recipient = frappe.get_value('Project', doc_name, 'project_manager')
	recipient = 'melissaraymond48@gmail.com'
	content = _('<p>Hi,</p><p>{0} would like to change his shipping address for the Sales Order <a href="https://en-dev.shei.sh/desk#Form/Sales%20Order/{1}" target="_blank">{1}</a></p> \
	<p>New Shipping Address: <a href="https://en-dev.shei.sh/desk#Form/Address/{2}" target="_blank">{2}</a></p>').format(customer, sales_order_name, shipping_address)
	subject = "Change Shipping Address for Project {0}".format(doc_name)
	send_email(recipient, subject, content)
	frappe.msgprint(_("Your request have been sent to your project manager."))

@frappe.whitelist()
def address_validation(address_title, address_line_1, address_city, address_country, checked_address_value):
	if((checked_address_value == 'Other') and (not address_title or not address_line_1 or not address_city or not address_country)):
		frappe.throw(_("You must filled all mandatory fields for the new address"))
	if frappe.db.exists('Address', "{0}-Shipping".format(address_title)):
		frappe.throw(_("Sorry, this address title already exist. Please choose something else"))