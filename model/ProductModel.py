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


class ProductModel:

    r"""
    product_id: ID único para identificar un producto.
    product_sku: Nombre de la tienda.
    product_unspc: Codigo unico de la tienda (puede ser alfanumerico).
    product_brand: Numero exterior del domicilio de la tienda.
    category_id: Calle y/o entrecalles del domicilio de la tienda.
    parent_category_id: Colonia del domicilio de la tienda.
    unit_of_measure: Ciudad del domicilio de la tienda.
    product_stock: Pais del domicilio de la tienda
    product_store_id: Codigo postal del domicilio de la tienda
    product_name: Inventario minimo aceptado en la tienda
    product_title: Titulo de un producto
    product_long_description: Descripcion larga del producto
    product_photo: URL de la imagen principal de un producto
    product_price: Precio del producto sin impuesto
    product_tax: Monto del impuesto del precio de un producto
    product_currency: Moneda de un precio para producto
    product_status: Define el estatus de un producto
    product_published: Define si el producto es publicado para la tienda
    product_manage_stock: Define si el producto maneja o no inventario en la tienda
    product_length: Altura del producto en centimetros
    product_width: Anchura del producto en centimetros
    product_height: Altura del producto en centimetros
    product_weight: Peso del producto en gramos
    creation_date: Fecha de alta del producto
    last_update_date: Fecha de actualizacion de los datos del producto
    """

    cfg = None

    product_id = int()
    product_sku = str()
    product_unspc = str()
    product_brand = str()
    category_id = int()
    parent_category_id = int()
    unit_of_measure = str()
    product_stock = int()
    product_store_id = str()
    product_name = str()
    product_title = str()
    product_long_description = str()
    product_photo = str()
    product_price = float()
    product_tax = float()
    product_currency = str()
    product_status = str()
    product_published = bool()
    product_manage_stock = bool()
    product_length = float()
    product_width = float()
    product_height = float()
    product_weight = float()
    creation_date = str()
    last_update_date = str()

    def __init__(self, sku, product_unspc, brand, category_id, parent_cat_id, uom, stock, store_id, name, title, long_desc,
                 photo, price, tax, currency, status, published, manage_stock, length, width, height, weight):
        self.product_id = uuid.uuid4().int
        self.product_sku = sku
        self.product_unspc = product_unspc
        self.product_brand = brand
        self.category_id = category_id
        self.parent_category_id = parent_cat_id
        self.unit_of_measure = uom
        self.product_stock = stock
        self.product_store_id = store_id
        self.product_name = name
        self.product_title = title
        self.product_long_description = long_desc
        self.product_photo = photo
        self.product_price = price
        self.product_tax = tax
        self.product_currency = currency
        self.product_status = status
        self.product_published = published
        self.product_manage_stock = manage_stock
        self.product_length = length
        self.product_width = width
        self.product_height = height
        self.product_weight = weight

    @classmethod
    def get_product_id(cls):
        return cls.product_id

    @classmethod
    def set_product_id(cls, product_id):
        cls.product_id = product_id

    @classmethod
    def get_product_sku(cls):
        return cls.product_sku

    @classmethod
    def set_product_sku(cls, product_sku):
        cls.product_sku = product_sku

    @classmethod
    def get_product_unspc(cls):
        return cls.product_unspc

    @classmethod
    def set_product_unspc(cls, product_unspc):
        cls.product_unspc = product_unspc

    @classmethod
    def get_product_brand(cls):
        return cls.product_brand

    @classmethod
    def set_product_brand(cls, product_brand):
        cls.product_brand = product_brand

    @classmethod
    def get_product_category_id(cls):
        return cls.category_id

    @classmethod
    def set_product_category_id(cls, product_category_id):
        cls.category_id = product_category_id

    @classmethod
    def get_product_parent_cat_id(cls):
        return cls.parent_category_id

    @classmethod
    def set_product_parent_cat_id(cls, product_parent_cat_id):
        cls.parent_category_id = product_parent_cat_id

    @classmethod
    def get_product_uom(cls):
        return cls.unit_of_measure

    @classmethod
    def set_product_uom(cls, product_uom):
        cls.unit_of_measure = product_uom

    @classmethod
    def get_product_stock(cls):
        return cls.product_stock

    @classmethod
    def set_product_stock(cls, product_stock):
        cls.product_stock = product_stock

    @classmethod
    def get_product_store_id(cls):
        return cls.product_store_id

    @classmethod
    def set_product_store_id(cls, product_store_id):
        cls.product_store_id = product_store_id

    @classmethod
    def get_product_name(cls):
        return cls.product_name

    @classmethod
    def set_product_name(cls, product_name):
        cls.product_name = product_name

    @classmethod
    def get_product_title(cls):
        return cls.product_title

    @classmethod
    def set_product_title(cls, product_title):
        cls.product_title = product_title

    @classmethod
    def get_product_long_desc(cls):
        return cls.product_long_description

    @classmethod
    def set_product_long_desc(cls, product_long_desc):
        cls.product_long_description = product_long_desc

    @classmethod
    def get_product_photo(cls):
        return cls.product_photo

    @classmethod
    def set_product_photo(cls, product_photo):
        cls.product_photo = product_photo

    @classmethod
    def get_product_price(cls):
        return cls.product_price

    @classmethod
    def set_product_price(cls, product_price):
        cls.product_price = product_price

    @classmethod
    def get_product_tax(cls):
        return cls.product_tax

    @classmethod
    def set_product_tax(cls, product_tax):
        cls.product_tax = product_tax

    @classmethod
    def get_product_currency(cls):
        return cls.product_currency

    @classmethod
    def set_product_currency(cls, product_currency):
        cls.product_currency = product_currency

    @classmethod
    def get_product_status(cls):
        return cls.product_status

    @classmethod
    def set_product_status(cls, product_status):
        cls.product_status = product_status

    @classmethod
    def get_product_published(cls):
        return cls.product_published

    @classmethod
    def set_product_published(cls, product_published):
        cls.product_published = product_published

    @classmethod
    def get_product_manage_stock(cls):
        return cls.product_manage_stock

    @classmethod
    def set_product_manage_stock(cls, product_manage_stock):
        cls.product_manage_stock = product_manage_stock

    @classmethod
    def get_product_length(cls):
        return cls.product_length

    @classmethod
    def set_product_length(cls, product_length):
        cls.product_length = product_length

    @classmethod
    def get_product_width(cls):
        return cls.product_width

    @classmethod
    def set_product_width(cls, product_width):
        cls.product_width = product_width

    @classmethod
    def get_product_height(cls):
        return cls.product_height

    @classmethod
    def set_product_height(cls, product_height):
        cls.product_height = product_height

    @classmethod
    def get_product_weight(cls):
        return cls.product_height

    @classmethod
    def set_product_weight(cls, product_weight):
        cls.product_weight = product_weight
