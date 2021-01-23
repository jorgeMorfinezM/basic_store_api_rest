# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"

import re
import json
from constants.constants import Constants as Const


class Utility:

    @staticmethod
    def validate_store_code_syntax(store_code):
        regex_store_code = r"^((A-Za-z){1})-(\d{2})$"

        math_store_code = re.match(regex_store_code, store_code, re.M | re.I)

        return math_store_code

    # Format Store Address
    @staticmethod
    def format_store_address(street_address,
                             external_number_address,
                             suburb_address,
                             zip_postal_code_address,
                             city_address,
                             country_address):
        address_store = "{} no. {}, col. {}, Cp. {}, {}, {}".format(street_address,
                                                                    external_number_address,
                                                                    suburb_address,
                                                                    zip_postal_code_address,
                                                                    city_address,
                                                                    country_address)

        return address_store

    @staticmethod
    def set_data_input_store_dict(id_store, code_store, name_store, street_store, ext_num_store, suburb_store,
                                  city_store, country_store, postal_code_store, minimum_stock):
        store_dict = {
            "store_id": id_store,
            "store_code": code_store,
            "store_name": name_store,
            "street_address": street_store,
            "external_number_address": ext_num_store,
            "suburb_address": suburb_store,
            "city_address": city_store,
            "country_address": country_store,
            "zip_postal_code_address": postal_code_store,
            "minimum_inventory": minimum_stock,
        }

        return json.dumps(store_dict)

    @staticmethod
    def set_data_input_product_dict(product_sku, product_unspc, product_brand, product_category_id,
                                    product_parent_category_id, product_uom, product_stock, product_store_code,
                                    product_name, product_title, product_long_description, product_photo, product_price,
                                    product_tax_price, product_currency, product_status, product_published,
                                    product_manage_stock, product_length, product_width, product_height, product_weight):

        product_dict = {
            'product_sku': product_sku,
            'product_unspc': product_unspc,
            'product_brand': product_brand,
            'category_id': product_category_id,
            'parent_category_id': product_parent_category_id,
            'unit_of_measure': product_uom,
            'product_stock': product_stock,
            'product_store_code': product_store_code,
            'product_name': product_name,
            'product_title': product_title,
            'product_long_description': product_long_description,
            'product_photo': product_photo,
            'product_price': product_price,
            'product_tax': product_tax_price,
            'product_currency': product_currency,
            'product_status': product_status,
            'product_published': product_published,
            'product_manage_stock': product_manage_stock,
            'product_length': product_length,
            'product_width': product_width,
            'product_height': product_height,
            'product_weight': product_weight,
        }

        return json.dumps(product_dict)

    @staticmethod
    def decimal_formatting(value):
        return ('%.2f' % value).rstrip('0').rstrip('.')

    # Define y obtiene el configurador para las constantes del sistema:
    @staticmethod
    def get_config_constant_file():
        """
        Get the config object to charge the constants configurator.

        :return object: cfg object, contain the Map to the constants allowed in Constants File configuration.
        """

        # PROD
        _constants_file = "/app/constants/constants.yml"

        # TEST
        # _constants_file = "/home/jorgemm/Documentos/tech_test_vacants/cargamos_api_test/constants/constants.yml"

        cfg = Const.get_constants_file(_constants_file)

        return cfg
