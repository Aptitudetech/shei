# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _

@frappe.whitelist()
def upload_wetransfer_link(doc_name, link):
	from frappe.email.doctype.email_template.email_template import get_email_template
	frappe.msgprint(_("Hey"))
	frappe.msgprint(_("Hey  --  {0}  --  {1}").format(doc_name, link))
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
