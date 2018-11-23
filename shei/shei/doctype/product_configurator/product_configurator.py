# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, division
import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

class ProductConfigurator(WebsiteGenerator):
	def calculate_final_price(self):
		self.set("product_configurator_items", [])
		product_configurator_items = frappe.get_all('Product Configurator Item', fields=['*'], filters={'parenttype': 'Product Configurator', 'parent': self.name})
		self.pc_total_panel_quantity = sum(t.item_quantity for t in product_configurator_items)

		self.pc_total_discount_pourcent = self.get_panel_qte_discount(self.pc_total_panel_quantity)

		for item in product_configurator_items:
			item.item_sqft_per_panel = (item.item_height * item.item_width) / 144
			item.item_sqft_price = self.get_sqft_per_panel_price(item.item_sqft_per_panel)
			item.item_base_panel_price = item.item_sqft_per_panel * item.item_sqft_price
			item.item_back_factor = self.get_back_factor(item.item_back)
			item.item_panel_price_w_back = item.item_base_panel_price * item.item_back_factor
			item.item_discount_pourcent = self.pc_total_discount_pourcent
			if item.item_discount_pourcent > 0:
				item.item_discount_dollar = (item.item_discount_pourcent / 100 ) * item.item_panel_price_w_back
			else:
				item.item_discount_dollar = 0
			item.item_discount_price = item.item_panel_price_w_back - item.item_discount_dollar
			item.item_line_price_cad = item.item_discount_price * item.item_quantity
			item.item_unit_price_cad = item.item_discount_price
			item.item_unit_price_usd = item.item_unit_price_cad / float(frappe.db.get_value('Product Configurator Setting', None, 'exchange_rate_usd'))
			item.item_total_sqft = item.item_sqft_per_panel * item.item_quantity
			item.item_total_studs = item.item_quantity * item.item_studs_per_panel
			item.item_total_av_nuts = item.item_quantity * item.item_av_nuts_per_panel
			item.item_studs_price = (item.item_studs_per_panel * self.get_misc_price('Studs')) * item.item_quantity
			item.item_av_nuts_price = (item.item_av_nuts_per_panel * self.get_misc_price('AV Nuts')) * item.item_quantity
			self.append("product_configurator_items", item)
		self.get_totals(product_configurator_items)

		self.save()
		frappe.msgprint("The price have been updated. To send this form to the client, please enter a valid email and check 'is published'")

	def get_totals(self, product_configurator_items = []):
		self.pc_total_line_price_cad = sum(t.item_line_price_cad for t in product_configurator_items)
		self.pc_line_total_unit_price_cad = sum(t.item_unit_price_cad for t in product_configurator_items)
		self.pc_total_unit_price_usd = sum(t.item_unit_price_usd for t in product_configurator_items)
		self.pc_total_sqft = sum(t.item_total_sqft for t in product_configurator_items)
		self.pc_total_sqft_per_panel = self.pc_total_sqft / self.pc_total_panel_quantity
		self.pc_total_sqft_price = self.pc_total_line_price_cad / self.pc_total_sqft
		self.pc_total_base_panel_price = sum(t.item_base_panel_price for t in product_configurator_items)
		if self.pc_total_discount_pourcent > 0:
			self.pc_discount_dollar = (self.pc_total_discount_pourcent / 100) * self.pc_total_base_panel_price
		else:
			self.pc_discount_dollar = 0
		self.pc_total_discount_price = self.pc_total_base_panel_price - self.pc_discount_dollar
		self.pc_total_studs = sum(t.item_total_studs for t in product_configurator_items)
		self.pc_total_av_nuts = sum(t.item_total_av_nuts for t in product_configurator_items)
		self.pc_total_studs_price = sum(t.item_studs_price for t in product_configurator_items)
		self.pc_total_av_nuts_price = sum(t.item_av_nuts_price for t in product_configurator_items)
		self.pc_studs_nuts_line_price_cad = self.pc_total_studs_price + self.pc_total_av_nuts_price
		self.pc_unit_price_cad = self.pc_studs_nuts_line_price_cad / self.pc_total_studs
		self.pc_unit_price_usd = self.pc_unit_price_cad / float(frappe.db.get_value('Product Configurator Setting', None, 'exchange_rate_usd'))

	def get_panel_qte_discount(self, quantity):
		discount = 0
		panel_discount_list = frappe.get_all('Discount Range Price', fields=['discount_percent', 'discount_range'], filters={ 'parenttype': 'Product Configurator Setting', 'parent': None })
		panel_discount_list.sort(key=self.sort_list_by_discount_range, reverse=False)
		for p in panel_discount_list:
			if quantity == p.discount_range:
				discount = p.discount_percent
				break
			if quantity > p.discount_range:
				discount = p.discount_percent
		return discount

	def get_misc_price(self, misc):
		misc_price = frappe.get_all('Misc Price', fields=['*'], filters={ 'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'misc_part':misc })
		if not misc_price[0].misc_price:
			frappe.throw("Sorry, the select misc have not been set yet. Please contact your administrator.") #Change the message eventually
		return misc_price[0].misc_price

	def get_back_factor(self, back):
		back_price = frappe.get_all('Back Price', ['*'], { 'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'back_finish':back })
		if not back_price[0].back_factor:
			frappe.throw("Sorry, the select back have not been set yet. Please contact your administrator.") #Change the message eventually
		return back_price[0].back_factor


	def get_sqft_per_panel_price(self, sqft_per_panel):
		price = 0
		sqft_per_panel = int(sqft_per_panel) #round the number down
		sqft_per_panel_list = frappe.get_all('Panel Price Range', fields=['panel_range', 'panel_price'], filters={ 'parenttype': 'Product Configurator Setting', 'parent': None })
		sqft_per_panel_list.sort(key=self.sort_list_by_panel_range, reverse=False)

		for p in sqft_per_panel_list:
			if sqft_per_panel == p.panel_range:
				price = p['panel_price']
				break
			if sqft_per_panel > p.panel_range:
				price = p['panel_price']
		return price

	def sort_list_by_discount_range(self, json_obj):
		try:
			return int(json_obj['discount_range'])
		except KeyError:
			return 0

	def sort_list_by_panel_range(self, json_obj):
		try:
			return int(json_obj['panel_range'])
		except KeyError:
			return 0

@frappe.whitelist()
def publish_document(email=None, doc_name=None):
	#from frappe.email.doctype.email_template.email_template import get_email_template
	frappe.get_doc('Product Configurator', doc_name).update({ 'is_published': True }).save()

	#user = frappe.new_doc('User')
	#user.update({
	#		"first_name": self.name,
	#		"email": email,
	#		"send_welcome_email": True
	#})
	#user.flags.ignore_permissions = True
	#user.save()
	#####self.db_set('is_published', True)
	#frappe.sendmail(
	#	recipients = [email],
	#	**get_email_template('SH Product Configurator', {'doc': doc_name})
	#)
	frappe.msgprint("The email have been sent to {0}".format(email))


@frappe.whitelist()
def unpublish_document(email=None, doc_name=None):
	#from frappe.email.doctype.email_template.email_template import get_email_template
	frappe.get_doc('Product Configurator', doc_name).update({ 'is_published': True }).save()


	#Desactivated the user/delete him?
	# frappe.db.get_all('Product Configurator', {'user_email' : email}, 'name')
	#user.update({
	#		"enabled": False,
	#})
	#user.flags.ignore_permissions = True
	#user.save()

	#frappe.sendmail(
	#	recipients = [email],
	#	**get_email_template('SH Product Configurator', {'doc': doc_name}) #Send an email to inform?
	#)
	frappe.msgprint("The client have no longer access to this document")
