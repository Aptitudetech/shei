# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.website.website_generator import WebsiteGenerator
from datetime import datetime
import easypost


class PriceConfigurator(Document):


	def validate(self):
		self.validate_panel()
		self.validate_graphic_section()

	def validate_graphic_section(self):
		if self.need_colour_match and not self.nb_colour_to_match:
			frappe.throw(_("You need to specify the number of color that needs to be matched"))
		if self.have_graphic_design and not self.graphic_design_nb_hours:
			frappe.throw(_("You need to specify the number of hours needed for the graphic design"))
		if self.have_technical_drawing and not self.technical_drawing_hours:
			frappe.throw(_("You need to specify the number of hours needed for the technical drawing"))
		if self.need_colour_match and not self.nb_colour_to_match:
			frappe.throw(_("You need to specify the number of color that needs to be matched"))

	def validate_panel(self):
		message = "You need to fill: <br>"
		row_index = 1
		for panel in self.get('price_configurator_items'):
	   		if not panel.item_is_not_panel:
				if panel.have_aluminium and not panel.aluminum_item:
					frappe.throw(_("{0} Aluminum Provided  - Row {1}").format(message, row_index))
				if not panel.height:
					frappe.throw(_("{0} Height  - Row {1}").format(message, row_index))
				if not panel.width:
					frappe.throw(_("{0} Width  - Row {1}").format(message, row_index))
				if not panel.qty:
					frappe.throw(_("{0} Quantity  - Row {1}").format(message, row_index))
				if not panel.back:
					frappe.throw(_("{0} Back  - Row {1}").format(message, row_index))
				if not panel.thickness:
					frappe.throw(_("{0} Thickness  - Row {1}").format(message, row_index))
				if panel.nb_panel_with_zclip > panel.qty:
					frappe.throw(_("{0} Number of panel with ZClip is highter than number of panel for that row  - Row {1}").format(message, row_index))
				if not panel.wallmount_kit_qty:
					frappe.throw(_("{0} Wallmount Kit Quantity  - Row {1}").format(message, row_index))
				if panel.panel_with_wallmount_lbracket > panel.qty:
					frappe.throw(_("{0} Number of panel with Wallmount LBracket is highter than number of panel for that row  - Row {1}").format(message, row_index))
				if not panel.cut:
					frappe.throw(_("{0} Cut  - Row {1}").format(message, row_index))
				if panel.is_cut_outsource and not panel.outsource_amount:
					frappe.throw(_("{0} Amount for the Outsource Cut  - Row {1}").format(message, row_index))
				if panel.discount_pourcent:
					min_discount, max_discount = self.get_discount_range(frappe.user_roles)
					if panel.discount_pourcent > max_discount or panel.discount_pourcent  <= min_discount:
						frappe.throw(_("You can only give a discount between {0} and {1}  - Row {0}").format(disc_min, disc_max))
			row_index = row_index + 1

	def get_discount_range(self, roles=[]):
		role_discount = frappe.db.get_all('Discount Range Price', fields=['role', 'min_discount_range', 'max_discount_range'], filters={ 'parenttype': 'Price Configurator Setting', 'parent': None })
		for discount in role_discount:
			if discount['role'] in roles:
				return discount['min_discount_range'], discount['max_discount_range']
		return 0,0

	#Entry Point : Calculate Final Price button
	def calculate_final_price(self):
        	panels = frappe.db.get_all('Price Configurator Item', fields=['*'], filters={'parenttype': 'Price Configurator', 'parent': self.name})
        	self.set_panel_data(panels)
        	self.get_total(panels)
		self.save()
        	frappe.msgprint(_("Your quote is now complete"))

	def set_panel_data(self, panels):
        	self.set("price_configurator_items", [])
		rate = self.get_exchange_rate()
        	for panel in panels:
        		panel.sqft_per_panel = self.convert_measurement_to_foot(panel.height) * self.convert_measurement_to_foot(panel.width)
			panel.total_sqft = panel.sqft_per_panel * panel.qty
            		panel.back_price = self.get_back_price(panel) * rate
            		panel.aluminium_price = self.get_aluminum_price(panel) * rate
            		panel.discount_dollar_customer_currency = panel.aluminium_price * panel.discount_pourcent * rate
			if panel.discount_dollar_customer_currency > 0:
	            		panel.discounted_price_customer_currency = panel.aluminium_price - panel.discount_dollar_customer_currency #already in customer currrency
			else:
				panel.discounted_price_customer_currency = 0
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
        		aluminium_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.item}, 'price_list_rate')
        	return aluminium_price * panel.sqft_per_panel

	def get_back_price(self, panel):
	        back_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':panel.back}, 'price_list_rate')
		back_unit = frappe.db.get_value('Item', {'item_code':panel.back}, 'stock_uom')
        	if back_unit == "SQFT":
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
        	price = 0
		if self.number_of_files > 1:
            		additional_file_qty = self.number_of_files - 1
            		additional_preflight_price = self.get_additionnal_preflight_price()
            		price = preflight_price + (additional_preflight_price * additional_file_qty)
        	return price

	def get_color_match_price(self, need_colour_match, nb_colour_to_match):
		price = 0
		if need_colour_match:
			colour_match_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'colour_match_item')
                        colour_match_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':colour_match_item}, 'price_list_rate')
                        price = colour_match_price * nb_colour_to_match
		return price

	def get_matching_mural_price(self, have_matching_mural):
		matching_mural_price = 0
		if have_matching_mural:
			matching_mural_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'matching_mural_item')
                        matching_mural_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': matching_mural_item}, 'price_list_rate')
		return matching_mural_price

	def get_graphic_design_price(self, have_graphic_design, graphic_design_nb_hours):
		price = 0
		if self.have_graphic_design:
			graphic_design_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'graphic_design_item')
                        graphic_design_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':graphic_design_item}, 'price_list_rate')
                        price = graphic_design_price * graphic_design_nb_hours
		return price

	def get_sample_with_order_price(self, sample_with_order_qty):
		price = 0
		if sample_with_order_qty > 0:
			sample_with_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'sample_with_order_item')
                        sample_with_order_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':sample_with_order_item}, 'price_list_rate')
                        price = sample_with_order_price * sample_with_order_qty
		return price

	def get_sample_without_order_price(self, sample_without_order_qty):
		price = 0
		if sample_without_order_qty > 0:
			sample_without_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'sample_without_order_item')
                        sample_without_order_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':sample_without_order_item}, 'price_list_rate')
                        price = sample_without_order_price * sample_without_order_qty
		return price

	def get_preflight_price(self):
		preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'preflight_item')
		price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': preflight_item}, 'price_list_rate') #even when there's no preflight, we charge one
		return price

	def get_additionnal_preflight_price(self):
		additionnal_preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'additionnal_preflight_item')
		price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code': additionnal_preflight_item}, 'price_list_rate')
                return price

	def get_total_studs_price(self, total_studs):
		studs_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'studs_item')
		studs_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':studs_item}, 'price_list_rate')
		return total_studs * studs_price

	def get_total_av_nuts_price(self, total_av_nuts):
		nuts_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'nuts_item')
		av_nuts_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':nuts_item}, 'price_list_rate')
                return total_av_nuts * av_nuts_price

	def get_total_tools_price(self, total_tools):
		tool_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'tool_item')
		tools = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':tool_item}, 'price_list_rate')
                return total_tools * tools

	def get_total_folds_price(self, total_folds):
		folds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'folds_item')
		folds_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':folds_item}, 'price_list_rate')
                return folds_price * total_folds

	def get_total_holes_price(self, total_holes):
		holds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'holds_item')
		holes_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':holds_item}, 'price_list_rate')
                return holes_price * total_holes

	def get_technical_drawing_price(self, have_technical_drawing, technical_drawing_hours):
		price = 0
		if have_technical_drawing:
			technical_drawing_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'technical_drawing_item')
			technical_drawing_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':technical_drawing_item}, 'price_list_rate')
                	price = technical_drawing_price * self.technical_drawing_hours
		return price

	def get_total_graphic_price(self):
		self.colour_match_price = self.get_color_match_price(self.need_colour_match, self.nb_colour_to_match)
            	self.matching_mural_price = self.get_matching_mural_price(self.have_matching_mural)
            	self.graphic_design_price = self.get_graphic_design_price(self.have_graphic_design, self.graphic_design_nb_hours)
            	self.sample_with_order_price = self.get_sample_with_order_price(self.sample_with_order_qty)
       		self.sample_without_order_price = self.get_sample_without_order_price(self.sample_without_order_qty)
        	self.preflight_price = self.get_preflight_price()
        	self.additional_preflight_price = self.get_additional_preflight_price(self.number_of_files, self.preflight_price)
        	self.total_studs_price = self.get_total_studs_price(self.total_studs)
        	self.total_av_nuts_price = self.get_total_av_nuts_price(self.total_av_nuts)
        	self.total_tools_price = self.get_total_tools_price(self.total_tools)
        	self.total_folds_price = self.get_total_folds_price(self.total_folds)
        	self.total_holes_price = self.get_total_holes_price(self.total_holes)
        	self.technical_drawing_price = self.get_technical_drawing_price(self.have_technical_drawing, self.technical_drawing_hours)
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
		lbracket_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'wallmount_lbracket_item')
        	lbracket_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':lbracket_item}, 'price_list_rate')
        	panel_height = self.convert_measurement_to_foot(panel.height)
        	panel_width = self.convert_measurement_to_foot(panel.width)
        	if panel_width >= 24:
            		nb_bracket = 4 #we need an extra zclip (*3)
        	return (panel_height * lbracket_price * nb_bracket) * panel.panel_with_wallmount_lbracket #price for all panels

    	def calculate_wallmount_kit_price(self, panel):
        	if panel.wallmount_kit == 0:
            		return
        	wallmount_kit_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'wallmount_kit_item')
		wallmount_kit_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':wallmount_kit_item}, 'price_list_rate')
        	panel_perimeter = 2 * (panel.width + panel.height)
        	panel_perimeter_foot = self.convert_measurement_to_foot(panel_perimeter)
        	wall_kit_price = wallmount_kit_price * panel_perimeter_foot
        	wall_kit_price = wall_kit_price * panel.wallmount_kit_qty
        	return wall_kit_price

	def calculate_zclip_price(self, panel):
	        if panel.zclip_qty == 0:
            		return
		zclip_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'zclip_item')
        	zclip_price = frappe.db.get_value('Item Price', {'price_list':'Standard Selling', 'item_code':zclip_item}, 'price_list_rate')
        	panel_max_height = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'zclip_max_height')
        	panel_height = self.convert_measurement_to_foot(panel.height)
		zclip_qty = 2
        	panel_width = self.convert_measurement_to_foot(panel.width)
        	if panel_height >= panel_max_height:
            		zclip_qty = zclip_qty + 1 #we need an extra zclip (*3)
        	zclip_price = (panel_width * zclip_price * zclip_qty) * panel.nb_panel_with_zclip
        	return zclip_price

	def test_api(self):
#		import httplib
#		import urllib

		self.test()
		return

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


	def get_abf_shipping_rate(self, shipper={}, consignee={}, shipment_info={}):
		import requests
		import xml.etree.ElementTree as ET

		r = requests.get("https://www.abfs.com/xml/aquotexml.asp?DL=2&ID=K4K155D4&ShipCity={shipper_city}&ShipState={shipper_state}&ShipZip={shipper_zipcode}&ShipCountry={shipper_country}&ConsCity={consignee_city}&ConsState={consignee_state}&ConsZip={consignee_zipcode}&ConsCountry={consignee_country}&Wgt1={total_weight}&Class1={shipment_class}&ShipAff={shipper_aff}&ShipMonth={ship_month}&ShipDay={ship_day}&ShipYear={ship_year}".format(shipper_city = shipper['city'], shipper_state=shipper['state'], shipper_zipcode=shipper['zipcode'], shipper_country=shipper['country'], consignee_city=consignee['city'], consignee_state=consignee['state'], consignee_zipcode=consignee['zipcode'], consignee_country=consignee['country'], total_weight=shipment_info['total_weight'], shipment_class=shipment_info['shipment_class'], shipper_aff=shipment_info['shipper_aff'], ship_month=shipment_info['ship_month'], ship_day=shipment_info['ship_day'], ship_year=shipment_info['ship_year']))
		root = ET.fromstring(r.text)
		try:
			abf_discount = float(root.find("DISCOUNTPERCENTAGE").text[:-1])
			abf_charge = float(root.find("CHARGE").text)
			amount_after_discount = round((abf_charge - (abf_charge * (abf_discount / 100))), 2)
			frappe.msgprint("abf_charge: {0}$ USD --- abf_discount: {1} --- amount_after_discount: {2}$ USD".format(abf_charge, abf_discount, amount_after_discount))
   		except AttributeError:
			frappe.msgprint(_("Rate Quote Error: <br>"))
   	    		for child in root.iter('ERRORMESSAGE'):
				frappe.msgprint(_("<li> {0} </li>").format(child.text))
			frappe.throw('Please fix those issues before proceeding')


	def format_pincode(self, country, pincode):
		if country == 'United States':
			try:
				formatted_pincode = int(pincode.replace(" ", ""))
			except ValueError:
				frappe.throw(_("The Postal Code for the consignee is invalid : {0}").format(pincode))
		if country == 'Canada':
			formatted_pincode = pincode.replace(" ", "").upper()
		return formatted_pincode

	def get_consignee_address(self):
		shipping_address_name = frappe.db.get_value('Quotation', {'price_configurator': self.name}, ['shipping_address_name', 'party_name'], as_dict=True)
		company = shipping_address_name.party_name
		shipping_address = frappe.db.get_value('Address', shipping_address_name.shipping_address_name, ['city', 'state', 'pincode', 'country', 'address_line1', 'address_line2', 'phone'], as_dict=True)
		country_code = frappe.db.get_value('Country', shipping_address.country, 'code')
		formatted_pincode = self.format_pincode(shipping_address.country, shipping_address.pincode)
		consignee = {
			"city": shipping_address.city,
			"state": shipping_address.state or "",
			"zipcode": formatted_pincode or "",
			"country": country_code,
			"street1": shipping_address.address_line1,
			"street2": shipping_address.address_line2 or "",
			"company": company,
			"phone": shipping_address.phone or "",
		}
		return consignee

	def get_shipper_address(self):
		country_code = frappe.db.get_value('Country', self.shipper_country, 'code')
		shipper = {
			"city": self.shipper_city,
			"state": self.shipper_state,
			"zipcode": self.format_pincode(self.shipper_country, self.shipper_zipcode),
			"country": country_code,
			"street1": self.shipper_street,
			"company": frappe.db.get_default("company"),
			"phone": self.shipper_phone
		}
		return shipper

	def get_formatted_date(self, date_str):
		system_date_format = frappe.defaults.get_user_default("date_format")
		#the system will always use 'yyyy', 'mm' and 'dd'. the only thing that will change is the order in which they appear
		system_date_format = system_date_format.replace("yyyy", "%Y").replace("mm", "%m").replace("dd","%d") 
		shipment_formatted_date = datetime.strptime(date_str, system_date_format)
		return shipment_formatted_date

	def get_shipment_info(self):
		shipment_date = self.get_formatted_date(self.shipment_date)
		shipment_info = {
                        "total_weight": 50,
                        "shipment_class": 50.0,
                        "shipper_aff": 'Y', #true if we are the shipper
                        "ship_month": shipment_date.month,
                        "ship_day": shipment_date.day,
                        "ship_year": shipment_date.year
                }
		return shipment_info

	def get_easypost_api_key(self):
		from frappe.utils import get_site_name
		site_name = get_site_name(frappe.local.request.host)
		if 'en-dev.' in site_name or 'en-staging' in site_name:
			return "EZTK2501b8a0157045088d3431005830d179E0Y0HFNP0lW0s6B43gxZHw"
		if 'en.shei.sh' in site_name:
			frappe.msgprint("PROD")


	def test(self):
		consignee = self.get_consignee_address()
		shipper = self.get_shipper_address()
		shipment_info = self.get_shipment_info()
		abf_rate = self.get_abf_shipping_rate(shipper, consignee, shipment_info)
		easypost.api_key = self.get_easypost_api_key()

		parcel = easypost.Parcel.create(
			length=20.2,
			width=10.9,
			height=5,
			weight=65.9
		)
		shipment = easypost.Shipment.create(
			to_address=consignee,
			from_address=shipper,
			parcel=parcel
		)
		shipment = easypost.Shipment.retrieve(shipment.id)
		for rate in shipment.get_rates().rates:
			frappe.msgprint(_("carrier RATE:  {0}   ---   currency RATE:  {1}   ---   RATEs:  {2}").format(rate.carrier, rate.currency, rate.rate))



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
	shipping_address = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', ['shipper_city', 'shipper_state', 'shipper_zipcode', 'shipper_country', 'shipper_street', 'shipper_phone'], as_dict=True)
	if quote_shipping_address:
		pc.update({
			'doctype_name': pc_name,
			'measurement': measurement,
			'preferred_currency': quote.currency,
			'consignee_city': quote_shipping_address.city,
			'consignee_state': quote_shipping_address.state,
			'consignee_zipcode': quote_shipping_address.pincode,
			'consignee_country': country,
			'shipper_city': shipping_address.shipper_city,
			'shipper_state': shipping_address.shipper_state,
			'shipper_zipcode': shipping_address.shipper_zipcode,
			'shipper_country': shipping_address.shipper_country,
			'shipper_street': shipping_address.shipper_street,
			'shipper_phone': shipping_address.shipper_phone
		})
	else:
		pc.update({
			'doctype_name': pc_name,
			'measurement': measurement,
			'preferred_currency': quote.currency,
			'shipper_city': shipping_address.shipper_city,
			'shipper_state': shipping_address.shipper_state,
			'shipper_zipcode': shipping_address.shipper_zipcode,
			'shipper_country': shipping_address.shipper_country,
			'shipper_street': shipping_address.shipper_street,
			'shipper_phone': shipping_address.shipper_phone
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

