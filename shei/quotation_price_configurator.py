# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def validate(doc):
    validate_panel(doc)
    validate_graphic_section(doc)


def validate_graphic_section(doc):
    if doc.need_colour_match and not doc.nb_colour_to_match:
        frappe.throw(_("You need to specify the number of color that needs to be matched"))
    if doc.have_graphic_design and not doc.graphic_design_nb_hours:
        frappe.throw(_("You need to specify the number of hours needed for the graphic design"))
    if doc.have_technical_drawing and not doc.technical_drawing_hours:
        frappe.throw(_("You need to specify the number of hours needed for the technical drawing"))


def validate_panel(doc):
    message = "You need to fill: <br>"
    row_index = 1
    for panel in doc.panel_list:
        if not panel.aluminum_item:
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
            frappe.throw(_(
                "{0} Number of panel with ZClip is highter than number of panel for that row  - Row {1}").format(
                message, row_index))
        if not panel.wallmount_kit_qty and panel.wallmount_kit_qty != 0:
            frappe.throw(_("{0} Wallmount Kit Quantity  - Row {1}").format(message, row_index))
        if panel.panel_with_wallmount_lbracket > panel.qty:
            frappe.throw(_(
                "{0} Number of panel with Wallmount LBracket is highter than number of panel for that row  - Row {1}").format(
                message, row_index))
        if not panel.cut:
            frappe.throw(_("{0} Cut  - Row {1}").format(message, row_index))
        row_index = row_index + 1


def get_aluminum_price(panel):
    if panel.have_aluminium == True:
        aluminium_price = frappe.db.get_value('Item Price',
                                              {'price_list': 'Standard Selling', 'item_code': panel.aluminum_item},
                                              'price_list_rate')
    else:
        aluminium_price = frappe.db.get_value('Item Price',
                                              {'price_list': 'Standard Selling', 'item_code': panel.item},
                                              'price_list_rate')
    return aluminium_price * panel.sqft_per_panel


def get_back_price(panel):
    back_details = frappe.db.get_value('Dropdown Options',
                                       {'doctype_type': 'Price Configurator Item', 'variable_name': 'back',
                                        'option_label': panel.back}, '*')
    back_price = 0
    if back_details.is_calculated_with_uom:
        if back_details.uom.lower() == 'sqft':
            back_price = float(back_details.option_value) * panel.sqft_per_panel
    else:
        back_price = float(back_details.option_value) * panel.qty
    return back_price


def get_thickness_price(panel):
    thickness_details = frappe.db.get_value('Dropdown Options',
                                            {'doctype_type': 'Price Configurator Item', 'variable_name': 'thickness',
                                             'option_label': panel.thickness}, '*')
    return float(thickness_details.option_value) * panel.sqft_per_panel


def get_cut_price(panel):
    cut_details = frappe.db.get_value('Dropdown Options',
                                      {'doctype_type': 'Price Configurator Item', 'variable_name': 'cut',
                                       'option_label': panel.cut}, '*')
    if cut_details.is_value_coming_from_user:
        cut_price = (panel.outsource_amount * 0.3) + panel.outsource_amount
    else:
        cut_price = float(cut_details.option_value) * int(panel.qty)
    return float(cut_price)


def get_color_match_price():
    colour_match_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                            'colour_match_item')
    colour_match_price = frappe.db.get_value('Item Price',
                                             {'price_list': 'Standard Selling', 'item_code': colour_match_item},
                                             'price_list_rate')
    return colour_match_price


def get_matching_mural_price():
    matching_mural_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                              'matching_mural_item')
    matching_mural_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling',
                                                              'item_code': matching_mural_item},
                                               'price_list_rate')
    return matching_mural_price


def get_graphic_design_price():
    graphic_design_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                              'graphic_design_item')
    graphic_design_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling',
                                                              'item_code': graphic_design_item},
                                               'price_list_rate')
    return graphic_design_price


def get_sample_with_order_price():
    sample_with_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                 'sample_with_order_item')
    sample_with_order_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling',
                                                                 'item_code': sample_with_order_item},
                                                  'price_list_rate')
    return sample_with_order_price


def get_sample_without_order_price():
    sample_without_order_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                    'sample_without_order_item')
    sample_without_order_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling',
                                                                    'item_code': sample_without_order_item},
                                                     'price_list_rate')
    return sample_without_order_price


def get_preflight_price():
    preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                         'preflight_item')
    price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': preflight_item},
                                'price_list_rate')  # even when there's no preflight, we charge one
    return price


def get_single_additional_preflight_price():
    additional_preflight_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                    'additionnal_preflight_item')
    price = frappe.db.get_value('Item Price',
                                {'price_list': 'Standard Selling', 'item_code': additional_preflight_item},
                                'price_list_rate')
    return price


def calculate_welding_price():
    welding_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                       'welding_item')
    welding_price = frappe.db.get_value('Item Price',
                                        {'price_list': 'Standard Selling', 'item_code': welding_item},
                                        'price_list_rate')
    return welding_price


def get_studs_price():
    studs_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'studs_item')
    studs_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': studs_item},
                                      'price_list_rate')
    return studs_price


def get_av_nuts_price():
    nuts_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'nuts_item')
    av_nuts_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': nuts_item},
                                        'price_list_rate')
    return av_nuts_price


def get_tools_price():
    tool_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'tool_item')
    tools = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': tool_item},
                                'price_list_rate')
    return tools


def get_folds_price():
    folds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'folds_item')
    folds_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': folds_item},
                                      'price_list_rate')
    return folds_price


def get_holes_price():
    holds_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'holds_item')
    holes_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': holds_item},
                                      'price_list_rate')
    return holes_price


def get_technical_drawing_price():
    technical_drawing_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                                 'technical_drawing_item')
    technical_drawing_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling',
                                                                 'item_code': technical_drawing_item},
                                                  'price_list_rate')
    return technical_drawing_price


def convert_measurement_to_foot(nb, measurement):
    if measurement == "MM":
        nb = float(nb) / 25.4
    if measurement == "CM":
        nb = float(nb) / 2.54
    if measurement == "Inches":
        nb = float(nb) / 12
    return nb


def get_lbracket_qty(panel, measurement):
    nb_bracket = 2
    panel_width = convert_measurement_to_foot(panel.width, measurement)
    if panel_width >= 24:
        nb_bracket = 4  # we need an extra zclip (*3)
    return nb_bracket * panel.panel_with_wallmount_lbracket


def get_lbracket_price(panel, measurement):
    lbracket_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                        'wallmount_lbracket_item')
    lbracket_price = frappe.db.get_value('Item Price',
                                         {'price_list': 'Standard Selling', 'item_code': lbracket_item},
                                         'price_list_rate')
    panel_height = convert_measurement_to_foot(panel.height, measurement)

    return panel_height * lbracket_price


def get_wallmount_kit_price(panel, measurement):
    if panel.wallmount_kit_qty == 0:
        return 0
    wallmount_kit_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                             'wallmount_kit_item')
    wallmount_kit_price = frappe.db.get_value('Item Price',
                                              {'price_list': 'Standard Selling', 'item_code': wallmount_kit_item},
                                              'price_list_rate')
    panel_perimeter = 2 * (panel.width + panel.height)
    panel_perimeter_foot = convert_measurement_to_foot(panel_perimeter, measurement)
    wall_kit_price = wallmount_kit_price * panel_perimeter_foot
    return wall_kit_price


def get_zclip_qty(panel, measurement):
    panel_max_height = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting',
                                           'zclip_max_height')
    panel_height = convert_measurement_to_foot(panel.height, measurement)
    zclip_qty = 2
    if panel_height >= panel_max_height:
        zclip_qty = zclip_qty + 1  # we need an extra zclip (*3)
    return zclip_qty * panel.nb_panel_with_zclip


def calculate_zclip_price(panel, measurement):
    if panel.nb_panel_with_zclip == 0:
        return 0
    zclip_item = frappe.db.get_value('Price Configurator Setting', 'Price Configurator Setting', 'zclip_item')
    zclip_price = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling', 'item_code': zclip_item},
                                      'price_list_rate')
    panel_width = convert_measurement_to_foot(panel.width, measurement)
    zclip_price = panel_width * zclip_price
    return zclip_price
