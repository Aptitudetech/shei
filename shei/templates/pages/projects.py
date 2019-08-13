# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
import datetime as dt
import re
from frappe.utils import get_site_name

@frappe.whitelist()
def upload_wetransfer_link(doc_name, link):
	"""Send the WeTransfer link by emil to the project manager"""
	recipient = frappe.get_value('Project', doc_name, 'project_manager')
	recipient = 'melissaraymond48@gmail.com'
	content = _('<p>Hi,</p><p>you received files from <a href="https://{0}/desk#Form/Project/{1}" target="_blank">{1}</a></p><p>To see them, please click this link: <a href="{2}" target="_blank">WeTransfer</a></p>').format(get_site_name(frappe.local.request.host), doc_name, link)
	subject = "Files Received for project {0}".format(doc_name)
	send_email(recipient, subject, content)

@frappe.whitelist()
def update_address_information(address_list = []):
	"""Update some information in each address related to the account"""
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
def create_shipping_address(address_title, address_line_1, address_city, address_zipcode, address_country, customer):
	address = frappe.new_doc('Address')
	address.update({
		"address_title": address_title,
		"address_line1": address_line_1,
		"city": address_city,
		"country": address_country,
		"pincode": address_zipcode,
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
def update_shipping_address(doc_name, sales_order_name, customer, address_line_1, address_city, address_zipcode, address_country, address_title, checked_address_value, address_info_list = []):
	address_validation(address_title, address_line_1, address_city, address_country, address_zipcode, checked_address_value)
	address_list = json.loads(address_info_list)
	update_address_information(address_list)
	if checked_address_value == 'Other':
		new_address = create_shipping_address(address_title, address_line_1, address_city, address_zipcode, address_country, customer)
		shipping_address = new_address.name
	else:
		shipping_address = checked_address_value
	if checked_address_value == frappe.db.get_value('Sales Order', sales_order_name, 'shipping_address_name'):
		return
	site = get_site_name(frappe.local.request.host)
	if 'en-dev' in site or 'en-staging':
		recipient = 'melissaraymond48@gmail.com'
	else:
		recipient = frappe.get_value('Project', doc_name, 'project_manager')
	content = _('<p>Hi,</p><p>{1} would like to change his shipping address for the Sales Order <a href="https://{0}/desk#Form/Sales%20Order/{2}" target="_blank">{2}</a></p> \
	<p>New Shipping Address: <a href="https://{0}/desk#Form/Address/{3}" target="_blank">{3}</a></p>').format(site, customer, sales_order_name, shipping_address)
	subject = "Change Shipping Address for Project {0}".format(doc_name)
	send_email(recipient, subject, content)
	frappe.msgprint(_("Your request have been sent to your project manager."))

@frappe.whitelist()
def address_validation(address_title, address_line_1, address_city, address_country, address_zipcode, checked_address_value):
	if((checked_address_value == 'Other') and (not address_title or not address_line_1 or not address_city or not address_country or not address_zipcode)):
		frappe.throw(_("Fill all mandatory fields for the new address"))
	if frappe.db.exists('Address', "{0}-Shipping".format(address_title)):
		frappe.throw(_("Sorry, this address title already exist. Please choose something else"))

@frappe.whitelist()
def create_contact(customer, contact_first_name, contact_last_name, contact_email, contact_phone):
	contact = frappe.new_doc('Contact')
	contact.update({
		"first_name": contact_first_name,
		"last_name": contact_last_name,
		"email_id": contact_email,
		"phone": contact_phone,
		"links": [{
			'link_doctype': 'Customer',
			'link_name': customer,
		}],
	})
	contact.flags.ignore_permissions = True
	contact.save()
	return contact

@frappe.whitelist()
def update_contact(doc_name, customer, contact_first_name, contact_last_name, 
					contact_email, contact_phone, contact_mobile, contact_department, 
					contact_title, checked_contact_value, so_name):
	#there's some Sales Order who don't have a contact. When updating the address, this method is also trigger.
	#We don't want to process the method if the value haven't changed
	if not checked_contact_value or checked_contact_value == frappe.db.get_value('Sales Order', so_name, 'contact_display'):
		return
	contact_validation(customer, contact_first_name, contact_last_name, contact_email, contact_phone, checked_contact_value)
	if checked_contact_value == 'Other':
		new_contact = create_contact(customer, contact_first_name, contact_last_name, contact_email, contact_phone)
		contact_name = new_contact.name
		contact_full_name = "{0} {1}".format(contact_first_name, contact_last_name)
	else:
		contact_name = "{0}-{1}".format(checked_contact_value, customer)
		contact_full_name = checked_contact_value
	site = get_site_name(frappe.local.request.host)
	if 'en-dev' in site or 'en-staging' in site:
		recipient = 'melissaraymond48@gmail.com'
	else:
		recipient = frappe.get_value('Project', doc_name, 'project_manager')

	content = _('<p>Hi,</p><p>{1} would like to change his contact for the Sales Order <a href="https://{0}/desk#Form/Sales%20Order/{2}" target="_blank">{2}</a></p> \
	<p>New Contact: <a href="https://{0}/desk#Form/Contact/{3}" target="_blank">{3}</a></p>').format(site, customer, so_name, contact_name)
	subject = "Change project contact person {0}".format(doc_name)
	send_email(recipient, subject, content)
	frappe.msgprint(_("Your request has forwarded to a project manager."))

@frappe.whitelist()
def contact_validation(customer, contact_first_name, contact_last_name, contact_email, contact_phone, checked_contact_value):
	if((checked_contact_value == 'Other') and (not contact_first_name or not contact_last_name or not contact_email or not contact_phone)):
		frappe.throw(_("Fill all mandatory fields for new contact"))
	email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', contact_email)
	if((checked_contact_value == 'Other') and (not email)):
		frappe.throw(_("The given email is invalid: {0}").format(contact_email))
