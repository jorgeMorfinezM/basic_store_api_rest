# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"


from constants.constants import Constants
import uuid


class StoreModel:

    r"""
    id_store: UUID único para identificar una tienda
    store_name: Nombre de la tienda
    store_code: Codigo unico de la tienda (puede ser alfanumerico)
    store_external_number: Numero exterior del domicilio de la tienda
    store_street_address: Calle y/o entrecalles del domicilio de la tienda
    store_suburb_address: Colonia del domicilio de la tienda
    store_city_address: Ciudad del domicilio de la tienda
    store_country_address: Pais del domicilio de la tienda
    store_zippostal_code: Codigo postal del domicilio de la tienda
    store_min_inventory: Inventario minimo aceptado en la tienda
    creation_date: Fecha de alta de la tienda
    last_update_date: Fecha de actualizacion de los datos de tienda
    """

    cfg = None

    id_store = str()
    store_code = str()
    store_name = str()
    store_external_number = str()
    store_street_address = str()
    store_suburb_address = str()
    store_city_address = str()
    store_country_address = str()
    store_zippostal_code = str()
    store_min_inventory = int()
    creation_date = str()
    last_update_date = str()

    def __init__(self,
                 code_store,
                 name_store,
                 external_number_store,
                 street_address,
                 suburb_address,
                 city_address,
                 country_address,
                 zip_code_address,
                 minimum_inventory,
                 creation_date,
                 last_update_date):
        self.cfg = self.get_config_constant_file()

        self.id_store = uuid.uuid4()
        self.store_code = code_store
        self.store_name = name_store
        self.store_external_number = external_number_store
        self.store_street_address = street_address
        self.store_suburb_address = suburb_address
        self.store_city_address = city_address
        self.store_country_address = country_address
        self.store_zippostal_code = zip_code_address
        self.store_min_inventory = minimum_inventory
        self.creation_date = creation_date
        self.last_update_date = last_update_date

    # getter method
    @classmethod
    def get_id_store(cls):
        return cls.id_store

    # setter method
    @classmethod
    def set_id_store(cls, store_id):
        cls.id_store = store_id

    # getter method
    @classmethod
    def get_store_code(cls):
        return cls.store_code

    # setter method
    @classmethod
    def set_store_code(cls, code_store):
        cls.store_code = code_store

    # getter method
    @classmethod
    def get_store_name(cls):
        return cls.store_name

    # setter method
    @classmethod
    def set_store_name(cls, name_store):
        cls.store_name = name_store

    # getter method
    @classmethod
    def get_external_number(cls):
        return cls.store_external_number

    # setter method
    @classmethod
    def set_external_number(cls, external_number_address):
        cls.store_external_number = external_number_address

    # getter method
    @classmethod
    def get_street_address(cls):
        return cls.store_street_address

    # setter method
    @classmethod
    def set_street_address(cls, street_address):
        cls.store_street_address = street_address

    # getter method
    @classmethod
    def get_suburb_address(cls):
        return cls.store_suburb_address

    # setter method
    @classmethod
    def set_suburb_address(cls, suburb_address):
        cls.store_suburb_address = suburb_address

    # getter method
    @classmethod
    def get_city_address(cls):
        return cls.store_city_address

    # setter method
    @classmethod
    def set_city_address(cls, city_address):
        cls.store_city_address = city_address

    # getter method
    @classmethod
    def get_country_address(cls):
        return cls.store_country_address

    # setter method
    @classmethod
    def set_country_address(cls, country_address):
        cls.store_country_address = country_address

    # getter method
    @classmethod
    def get_zip_postal_address(cls):
        return cls.store_zippostal_code

    # setter method
    @classmethod
    def set_zip_postal_address(cls, zip_postal_address):
        cls.store_zippostal_code = zip_postal_address

    # getter method
    @classmethod
    def get_minimum_stock(cls):
        return cls.store_min_inventory

    # setter method
    @classmethod
    def set_minimum_stock(cls, minimum_stock):
        cls.store_min_inventory = minimum_stock

    def validate_store_stock(self, product_stock):
        stock_valid = False
        if product_stock >= self.store_min_inventory:
            stock_valid = True
        return stock_valid

    # Define y obtiene el configurador para las constantes del sistema:
    @classmethod
    def get_config_constant_file(cls):
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

        cls.cfg = Constants.get_constants_file(_constants_file)

        return cls.cfg
