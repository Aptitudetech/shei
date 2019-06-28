# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
#import easypost

class PriceConfigurator(Document):

	def convert_to_quote_btn(self):
		quote = frappe.get_doc('Quotation', {'price_configurator': self.name})
		frappe.msgprint(_("111 quote: {0}").format(quote.name))
		

		frappe.msgprint("OK")


	#Entry Point : Calculate Final Price button
	def calculate_final_price(self):
        	panels = frappe.db.get_all('Price Configurator Item', fields=['*'], filters={'parenttype': 'Price Configurator', 'parent': self.name})
        	self.set_panel_data(panels)
        	self.get_total(panels)
		self.save()

	def set_panel_data(self, panels):
        	self.set("price_configurator_items", [])
		rate = self.get_exchange_rate()
        	for panel in panels:
        		panel.sqft_per_panel = self.convert_measurement_to_foot(panel.height) * self.convert_measurement_to_foot(panel.width)
			panel.total_sqft = panel.sqft_per_panel * panel.qty
            		panel.back_price = self.get_back_price(panel) * rate
            		panel.aluminium_price = self.get_aluminum_price(panel) * rate
            		panel.discount_dollar_customer_currency = panel.aluminium_price * panel.discount_pourcent * rate
            		panel.discounted_price_customer_currency = panel.aluminium_price - panel.discount_dollar_customer_currency #already in customer currrency
            		panel.thickness_price = self.get_thickness_price(panel) * rate
            		panel.cut_price = self.get_cut_price(panel.outsource_amount, panel) * rate
            		panel.zclip_price = self.calculate_zclip_price(panel) * rate
            		panel.wallmount_kit_price = self.calculate_wallmount_kit_price(panel) * rate
            		panel.wallmount_lbracket_price = self.calculate_lbracket_price(panel) * rate
            		panel.line_price_customer_currency = panel.aluminium_price + panel.back_price + panel.thickness_price + panel.cut_price + panel.zclip_price + panel.wallmount_kit_price + panel.wallmount_lbracket_price
			panel.line_price_cad = panel.line_price_customer_currency / rate
            		self.append("price_configurator_items", panel)
        	return panels

	def convert_panel_price_to_customer_currency(self, panel):
	        if self.preferred_currency == frappe.defaults.get_user_default("Currency"):
        		panel.line_price_customer_currency = panel.line_price_cad #the prices are already in CAD, no changes required
	            	return panel
        	rate = self.get_exchange_rate()
        	panel.back_price = panel.back_price * rate
        	panel.aluminium_price = panel.aluminium_price * rate
        	panel.thickness_price = panel.thickness_price * rate
        	panel.cut_price = panel.cut_price * rate
        	panel.zclip_price = panel.zclip_price * rate
        	panel.wallmount_kit_price = panel.wallmount_kit_price * rate
        	panel.wallmount_lbracket_price = panel.wallmount_lbracket_price * rate
        	panel.line_price_customer_currency = panel.line_price_cad * rate
        	panel.discounted_price_customer_currency = panel.discounted_price_customer_currency * rate
		return panel

	def get_exchange_rate(self):
		if self.preferred_currency != frappe.defaults.get_user_default("Currency"):
	        	return frappe.db.get_value('Currency Exchange', {'from_currency':self.preferred_currency, 'to_currency':'CAD', 'for_selling':True}, ['exchange_rate'], order_by='creation desc') #takes the last created currency excahnge for the given currency
		return 1

    	def get_aluminum_price(self, panel):
        	if panel.have_aluminium == True:
            		aluminium_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.aluminum_item}, 'price_list_rate')
        	else:
        		aluminium_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.panel_item}, 'price_list_rate')
        	return aluminium_price * panel.sqft_per_panel

	def get_back_price(self, panel):
	        back_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.back}, 'price_list_rate')
        	if panel.back == "2S" or panel.back == "Sintra":
        		back_price = back_price * panel.sqft_per_panel
        	else:
            		back_price = back_price * panel.qty
        	return back_price

	def get_thickness_price(self, panel):
        	thickness = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.thickness}, 'price_list_rate')
        	return thickness * panel.sqft_per_panel

	def get_cut_price(self, amount, panel): #if not cut_price -> ie is outsource
        	if panel.is_cut_outsource:
            		cut_price = (amount * 0.3) + amount
        	else:
            		cut_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.cut}, 'price_list_rate') * panel.qty
        	return cut_price

    	def get_additional_preflight_price(self, nb_file, preflight_price):
        #The first file cost a certain amount, but any additionnal price willl be at a different price
        	if self.number_of_files > 1:
            		additional_file_qty = self.number_of_files - 1
            		additional_preflight_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': self.additionnal_preflight_item}, 'price_list_rate')
            		preflight_price = preflight_price + (additional_preflight_price * additional_file_qty)
        	return preflight_price or 0

	def get_total_graphic_price(self):
        #self.preflight_price = self.get_preflight_price(nb_file)
	        if self.need_colour_match:
            		colour_match_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.colour_match_item}, 'price_list_rate')
            		colour_match_price = colour_match_price * self.nb_colour_to_match
        	if self.have_matching_mural: #'matching for murals
            		matching_mural_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': self.matching_mural_item}, 'price_list_rate')
        	if self.have_graphic_design:
            		graphic_design_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.graphic_design_item}, 'price_list_rate')
            		graphic_design_price = graphic_design_price * self.graphic_design_nb_hours
		if self.sample_with_order_qty > 0:
            		sample_with_order_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.sample_with_order_item}, 'price_list_rate')
            		sample_with_order_price = sample_with_order_price * self.sample_with_order_qty
        	if self.sample_without_order_qty > 0:
            		sample_without_order_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.sample_without_order_item}, 'price_list_rate')
            		sample_without_order_price = sample_without_order_price * self.sample_without_order_qty
		self.sample_with_order_price = sample_with_order_price or 0
		self.sample_without_order_price = sample_without_order_price or 0
        	self.colour_match_price = colour_match_price or 0
        	self.preflight_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': self.preflight_item}, 'price_list_rate') #even when there's no preflight, we charge it
        	self.additional_preflight_price = self.get_additional_preflight_price(self.number_of_files, self.preflight_price)
        	studs_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.studs_item}, 'price_list_rate')
        	self.total_studs_price = self.total_studs * studs_price
        	av_nuts_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.nuts_item}, 'price_list_rate')
        	self.total_av_nuts_price = self.total_av_nuts * av_nuts_price
        	tools = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.tool_item}, 'price_list_rate')
        	self.total_tools_price = self.total_tools * tools
        	folds_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.folds_item}, 'price_list_rate')
        	self.total_folds_price = folds_price * self.total_folds
        	holes_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.holds_item}, 'price_list_rate')
        	self.total_holes_price = holes_price * self.total_holes
        	technical_drawing_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':self.technical_drawing_item}, 'price_list_rate')
        	self.technical_drawing_price = technical_drawing_price * self.technical_drawing_hours
        	return self.colour_match_price + self.preflight_price + self.additional_preflight_price + self.total_studs_price + self.total_av_nuts_price + self.total_tools_price + self.total_folds_price + self.total_holes_price + self.technical_drawing_price

	def get_other_price(self, panels=[]):
	        self.total_panel_quantity = sum(p.qty for p in panels)
	        self.total_sqft = sum(p.total_sqft for p in panels)
        	self.total_zclip_price = sum(p.zclip_price for p in panels)
        	self.total_wallmount_kit_price = sum(p.wallmount_kit_price for p in panels)
        	self.total_wallmount_kit_qty = sum(p.wallmount_kit_qty for p in panels)
        	self.total_wallmount_lbracket_price = sum(p.wallmount_lbracket_price for p in panels)
        	self.wallmount_lbracket_qty = sum(p.wallmount_lbracket_qty for p in panels)
        	return self.total_panel_quantity + self.total_zclip_price + self.total_wallmount_kit_price + self.total_wallmount_kit_qty + self.total_wallmount_lbracket_price + self.wallmount_lbracket_qty

    	def get_total(self, panels = []):
        	graphic_price = self.get_total_graphic_price()
        	other_price = self.get_other_price(panels)
        	self.total_line_price_cad = sum(p.line_price_cad for p in panels) + graphic_price + other_price
        	self.total_line_price_customer_currency = sum(p.line_price_customer_currency for p in panels) + (graphic_price + other_price) * self.get_exchange_rate()
        	self.discount_dollar = sum(p.discount_dollar for p in panels)
        	self.total_discounted_price_customer_currency = sum(p.discount_price for p in panels)
        	frappe.msgprint(_("Your quote is now complete"))

	def convert_measurement_to_foot(self, nb):
	        measurement = self.measurement
        	if measurement == "MM":
        		nb = nb / 25.4
        	if measurement == "CM":
            		nb = nb / 2.54
        	if measurement == "FEET":
            		nb = nb * 12
        	return nb

	def calculate_lbracket_price(self, panel):
	        if panel.wallmount_lbracket_qty == 0:
        		return
        	nb_bracket = 2
        	lbracket_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.wallmount_lbracket_item}, 'price_list_rate')
        	panel_height = self.convert_measurement_to_foot(panel.height)
        	panel_width = self.convert_measurement_to_foot(panel.width)
        	if panel_width >= 24:
            		nb_bracket = 4 #we need an extra zclip (*3)
        	return (panel_height * lbracket_price * nb_bracket) * panel.wallmount_lbracket_qty #price for all panels

    	def calculate_wallmount_kit_price(self, panel):
        	if panel.wallmount_kit == 0:
            		return
        	wallmount_kit_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.wallmount_kit_item}, 'price_list_rate')
        	panel_perimeter = 2 * (panel.width + panel.height)
        	panel_perimeter_foot = self.convert_measurement_to_foot(panel_perimeter)
        	wall_kit_price = wallmount_kit_price * panel_perimeter_foot
        	wall_kit_price = wall_kit_price * panel.qty
        	return wall_kit_price

	def calculate_zclip_price(self, panel):
	        if panel.zclip_qty == 0:
            		return
        	zclip_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.zclip_item}, 'price_list_rate')
        	nb_zclip = 2
        	panel_max_height = 72
        	panel_height = self.convert_measurement_to_foot(panel.height)
        	panel_width = self.convert_measurement_to_foot(panel.width)
        	if panel_height >= panel_max_height:
            		nb_zclip = 3 #we need an extra zclip (*3)
        	zclip_price = (panel_width * zclip_price * nb_zclip) * panel.qty #price for all panel
        	return zclip_price



	def test_api(self):
		import httplib
		import urllib

		conn = httplib.HTTPConnection(host='www.packit4me.com', port=80)
		frappe.msgprint(_("conn: {0}").format(conn))

		params =  urllib.urlencode({'bins': '0:0:10x10x10', 'items': ['0:0:0:1x1x1', '1:0:0:3x3x3', '2:0:0:2x2x2']})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		conn.request("POST", "/api/call/raw", params, headers)
		content = conn.getresponse().read()
		conn.close()
		frappe.msgprint(_("Content: {0}").format(content))



		conn = httplib.HTTPConnection(host='www.packit4me.com', port=80)
		params =  urllib.urlencode({'bins': '0:0:10x10x10', 'items': ['0:0:0:1x1x1', '1:0:0:3x3x3', '2:0:0:2x2x2'], 'binId':'0'})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"}
		conn.request("POST", "/api/call/preview", params, headers)
		content = conn.getresponse().read()
		conn.close()
		#frappe.msgprint(_("Content: <code> {0} </code>").format(str(content)))

		#frappe.msgprint(_("""
		#<iframe id="serviceFrameSend" src={0} width="1000" height="1000"  frameborder="0">
	#		""").format(content))



		return content

	def test(self):
		import requests
		import xml.etree.ElementTree as ET

		content = self.test_api()
		return content


		if self.is_default_shipper_address:
			shipper_city = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_city')
			shipper_state = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_state')
			shipper_zipcode = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_zipcode')
			shipper_country = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_country')
		else:
			shipper_city = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_city')
			shipper_state = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_state')
			shipper_zipcode = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_zipcode')
			shipper_country = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'shipper_country')
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



@frappe.whitelist()
#Called from Quotation -> 'Create Price Configurator'
def create_price_configurator(quote_name = None):
	"""Create a Price Configurator based on the data in Quotation"""
	quote = frappe.get_doc('Quotation', quote_name)
	quote_shipping_address = frappe.db.get_value('Address', quote.shipping_address_name, ['city', 'country', 'state', 'pincode'], as_dict=True)
	pc_name = frappe.db.get_value('Quotation', quote_name, 'price_configurator')
	if pc_name:
		version = len(pc_name.split('v'))
		if version == 1:
			pc_name = pc_name + 'v1'
		else:
			nb = int(pc_name.split('v')[1])
			nb = nb + 1
			pc_name = "PC-" + quote_name.split("-")[1] + 'v' + str(nb)
	else:
		pc_name = "PC-" + quote_name.split("-")[1]
    
	pc = frappe.new_doc('Price Configurator')
	#Set default measurement and country
	country = quote_shipping_address['country']
	measurement = 'MM'
	if quote_shipping_address:
		pc.update({
			'doctype_name': pc_name,
			'measurement': measurement,
			'preferred_currency': quote.currency,
			'consignee_city': quote_shipping_address.city,
			'consignee_state': quote_shipping_address.state,
			'consignee_zipcode': quote_shipping_address.pincode,
			'consignee_country': country,
		})
	else:
		pc.update({
			'doctype_name': pc_name,
			'measurement': measurement,
			'preferred_currency': quote.currency,
		})
	pc.flags.ignore_permissions = True
	pc.save()
	quote.update({ 'price_configurator' : pc_name})
	quote.flags.ignore_permissions = True
	quote.save()
	frappe.msgprint(_("The Price Configurator have been added to the quote"))


#@frappe.whitelist()
#def make_quotation(source_name, target_doc=None):
#	doclist = get_mapped_doc("Price Configurator", source_name, {
#		"Supplier Quotation": {
#			"doctype": "Quotation",
#			"field_map": {
#				"name": "supplier_quotation",
#			}
#		},
#		"Supplier Quotation Item": {
#			"doctype": "Quotation Item",
#			"condition": lambda doc: frappe.db.get_value("Item", doc.item_code, "is_sales_item")==1,
#			"add_if_empty": True
#		}
#	}, target_doc)
#
#	return doclist

