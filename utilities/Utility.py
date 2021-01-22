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
from constants.constants import Constants as Const


class Utility:

    @staticmethod
    def validate_store_code_syntax(store_code):
        regex_store_code = r"^((A-Za-z){1})-(\d{2})$"

        math_store_code = re.match(regex_store_code, store_code, re.M | re.I)

        if math_store_code:
            return True

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

    # Define y obtiene el configurador para las constantes del sistema:
    @staticmethod
    def get_config_constant_file():
        """
        Contiene la obtencion del objeto config
        para setear datos de constantes en archivo
        configurador.

        :return object: ocfg object, contain the Map to the constants allowed in Constants File configuration.
        """

        # PROD
        _constants_file = "/app/constants/constants.yml"

        # TEST
        # _constants_file = "/home/jorgemm/Documentos/PycharmProjects/urbvan_microservice_test/constants/constants.yml"

        cfg = Const.get_constants_file(_constants_file)

        return cfg