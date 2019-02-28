# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, division
import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
import easypost

class ProductConfigurator(WebsiteGenerator):

	def validate(self):
		frappe.msgprint("here?")
		for item in self.get("product_configurator_items"):
			product = frappe.db.get_value("Environment", item.item_product, "product")
			thickness_product = frappe.get_value('Panel Thickness', {'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'name': item.item_panel_thickness}, 'product')
			finish_product = frappe.get_value('Panel Finish', {'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'name': item.item_panel_finish}, 'product')
			cut_product = frappe.get_value('Panel Cut', {'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'name': item.item_panel_cut}, 'product')
			back_product = frappe.get_value('Panel Back', {'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting', 'name': item.item_back}, 'product')

			for product_identifiers in [thickness_product, finish_product, cut_product, back_product]:
				if product != product_identifiers:
					frappe.throw(_("Sorry, the environment, thickness, finish, cut and back of a product should be the same. <br> Problematic row: <strong>{0}</strong>").format(item.idx))
		frappe.msgprint("here?2")


	def get_item(self, item2):
		#final_item_name = "FOLIA|ALTO" + item.item_product + "E -" + "thickness : item_panel_thickness" + "finish : item_panel_finish" + " Back: item_back" + "Cut: item_panel_cut"
		self.set("product_configurator_items", [])
		product_configurator_items = frappe.get_all('Product Configurator Item', fields=['*'], filters={'parenttype': 'Product Configurator', 'parent': self.name})

		for item in product_configurator_items:
			product_name = item.item_product.split(" - ")[1].upper()
			env  = item.item_product[0].upper()
			thickness = item.item_panel_thickness.split(" - ")[0]

			frappe.msgprint(_("PN: {0}, ENV: {1}, Thick: {2}").format(product_name, env, thickness))

			pcs = frappe.get_all('Panel Finish', fields=['panel_finish_abr'], filters={'parenttype': 'Product Configurator Setting', 'parent': 'Product Configurator Setting'})
            #* Deposit Setting = Name of the Child Doctype
            #* Customer Deposit Setup = Name of Main Doctype

			frappe.throw(pcs)

			finish = item.item_panel_finish #get abr
			back = item.item_back # get abv
			cut = item.item_panel_cut # get abr

	def test(self):
		import requests
		import xml.etree.ElementTree as ET
		shipper_city = 'Huntingdon'
		shipper_state = 'QC'
		shipper_zipcode = 'J0S1H0'
		shipper_country = 'CA'
		consignee_city = 'TULSA'
		consignee_state = 'OK'
		consignee_zipcode = 74104
		consignee_country = 'US'
		total_weight = 50
		shipment_class = 50.0
		shipper_aff = 'Y' #true if we are the shipper
		ship_month = 2
		ship_day = 10
		ship_year = 2019


	#US Only: https://www.zipcodeapi.com/rest/rw3tf9DjeiMpy77gvjfg6qO5cU87GjMYp1PynQUijIPHZ6QFMXUdnLbT4iUv5mzf/info.json/85001/degrees  where 85001 = zipcode

		r = requests.get("https://www.abfs.com/xml/aquotexml.asp?DL=2&ID=K4K155D4&ShipCity={shipper_city}&ShipState={shipper_state}&ShipZip={shipper_zipcode}&ShipCountry={shipper_country}&ConsCity={consignee_city}&ConsState={consignee_state}&ConsZip={consignee_zipcode}&ConsCountry={consignee_country}&Wgt1={total_weight}&Class1={shipment_class}&ShipAff={shipper_aff}&ShipMonth={ship_month}&ShipDay={ship_day}&ShipYear={ship_year}".format(shipper_city = shipper_city, shipper_state=shipper_state, shipper_zipcode=shipper_zipcode, shipper_country=shipper_country, consignee_city=consignee_city, consignee_state=consignee_state, consignee_zipcode=consignee_zipcode, consignee_country=consignee_country, total_weight=total_weight, shipment_class=shipment_class, shipper_aff=shipper_aff, ship_month=ship_month, ship_day=ship_day, ship_year=ship_year))
		root = ET.fromstring(r.text)
		try:
			abf_dicount = float(root.find("DISCOUNTPERCENTAGE").text[:-1])
			abf_charge = float(root.find("CHARGE").text)
			amount_before_discount = round(((abf_charge / (100 - abf_dicount)) * 100), 2)
			frappe.throw("abf_charge: {0} <br> abf_dicount: {1} <br> amount_before_discount: {2}".format(abf_charge, abf_dicount, amount_before_discount))
   		except AttributeError:
			frappe.msgprint(_("Rate Quote Error: <br>"))
   	    		for child in root.iter('ERRORMESSAGE'):
				frappe.msgprint(_("<li> {0} </li>").format(child.text))
			frappe.throw('Please fix those issues before proceeding')

		easypost.api_key = "EZTK2501b8a0157045088d3431005830d179E0Y0HFNP0lW0s6B43gxZHw" #DEV
		# create address
		to_address = easypost.Address.create(
			street1="417 Montgomery Street",
			street2="FLOOR 5",
			city="San Francisco",
			state="CA",
			zip="94104",
			country="US",
			company="EasyPost",
			phone="415-456-7890"
		)
		from_address = easypost.Address.create(
			street1="UNDELIEVRABLE ST",
			city="San Francisco",
			state="CA",
			zip="94104",
			country="US",
			company="EasyPost2",
			phone="222-222-7890"
		)
		parcel = easypost.Parcel.create(
			length=20.2,
			width=10.9,
			height=5,
			weight=65.9
		)
		shipment = easypost.Shipment.create(
			to_address=to_address,
			from_address=from_address,
			parcel=parcel
		)
		ship_id = shipment.id
		shipment = easypost.Shipment.retrieve(ship_id)

		for rate in shipment.get_rates().rates:
			carrier = rate.carrier,
			currency = rate.currency,
			rate_price = rate.rate

			frappe.msgprint(_("carrier RATE:  {0}").format(carrier))
			frappe.msgprint(_("currency RATE:  {0}").format(currency))
			frappe.msgprint(_("RATEs:  {0}").format(rate_price))



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
			#item.item_total_studs = item.item_quantity * item.item_studs_per_panel
			#item.item_total_av_nuts = item.item_quantity * item.item_av_nuts_per_panel
			#item.item_studs_price = (item.item_studs_per_panel * self.get_misc_price('Studs')) * item.item_quantity
			#item.item_av_nuts_price = (item.item_av_nuts_per_panel * self.get_misc_price('AV Nuts')) * item.item_quantity
			self.append("product_configurator_items", item)
		self.get_totals(product_configurator_items)

		self.save()
		frappe.msgprint("The price have been updated")

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
