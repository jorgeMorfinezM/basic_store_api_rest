# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A19.1 ($Rev: 1 $)"

import json
import re
import threading
import time
import uuid

from flask import Flask, jsonify, render_template, json, request
from flask_jwt_extended import JWTManager

from auth_controller.api_authentication import *
from utilities.Utility import Utility as Util
from logger_controller.logger_control import *
from db_controller.database_backend import *
from model.StoreModel import StoreModel
from model.ProductModel import ProductModel


logger = configure_ws_logger()


app = Flask(__name__, static_url_path='/static')

app.config['JWT_SECRET_KEY'] = 'ap1_v3h1cl3_urv4n_m1cr0_t3st'
app.config['JWT_BLACKLIST_ENABLED'] = False
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)


# Se inicializa la App con un hilo para evitar problemas de ejecución
# (Falta validacion para cuando ya exista hilo corriendo)
@app.before_first_request
def activate_job():
    def run_job():
        while True:
            time.sleep(2)

    thread = threading.Thread(target=run_job)
    thread.start()


# Contiene la llamada al HTML que soporta la documentacion de la API,
# sus metodos, y endpoints con los modelos de datos I/O
@app.route('/')
def main():

    return render_template('api_manage_ecommerce.html')


def get_stock_all_stores_by_product(product_sku):

    stock_list = []

    stock_in_stores = select_all_stock_in_product(product_sku)

    stock_list = json.loads(stock_in_stores)

    if stock_list:

        logger.info('List Stock in all Stores by SKU: {}: {}: '.format(product_sku, stock_list))

        return stock_list


@app.route('/api/ecommerce/stock/total/',  methods=['GET', 'OPTIONS'])
@jwt_required
def endpoint_list_stock_all_stores():

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return request_unauthorized()
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        elif request.method == 'GET':

            data = request.get_json(force=True)

            product_sku = data['product_sku']

            json_data = get_stock_all_stores_by_product(product_sku)

            if not product_sku:
                return request_conflict()

            return json.dumps(json_data)

        else:
            return not_found()


def get_stock_by_store_by_product(product_sku, store_code):

    stock_list = []

    stock_in_store = select_stock_in_product(store_code, product_sku)

    stock_list = json.loads(stock_in_store)

    if stock_list:

        logger.info('List Stock in one Store: {} by SKU: {}: {}: '.format(store_code, product_sku, stock_list))

        return stock_list


@app.route('/api/ecommerce/stock/detail/',  methods=['GET', 'OPTIONS'])
@jwt_required
def endpoint_detailed_stock_by_sku():

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return request_unauthorized()
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        elif request.method == 'GET':

            data = request.get_json(force=True)

            product_sku = data['product_sku']
            store_code = data['store_code']

            json_data = get_stock_by_store_by_product(product_sku, store_code)

            if not product_sku:
                return request_conflict()

            return json.dumps(json_data)

        else:
            return not_found()


def add_stock_by_store_by_product(stock, product_sku, store_code):

    stock_add = []

    stock_in_product = update_product_store_stock(stock, product_sku, store_code)

    stock_add = json.loads(stock_in_product)

    if stock_add:

        logger.info('Add Stock: {} in one Product: {} by Store: {}: {}: '.format(stock,
                                                                                 product_sku,
                                                                                 store_code,
                                                                                 stock_add))

        return stock_add


@app.route('/api/ecommerce/stock/add/',  methods=['POST', 'OPTIONS'])
@jwt_required
def endpoint_update_stock():

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return request_unauthorized()
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        elif request.method == 'GET':

            data = request.get_json(force=True)

            stock = data['stock']
            product_sku = data['product_sku']
            store_code = data['store_code']

            json_data = add_stock_by_store_by_product(stock, product_sku, store_code)

            if not product_sku and not store_code and not stock:
                return request_conflict()

            return json.dumps(json_data)

        else:
            return not_found()


def manage_store_requested_data(store_data):

    store_data_manage = []

    store_model_db = StoreModelDb()

    try:

        store_code = store_data.get("store_code")
        store_name = store_data.get("store_name")
        store_street_address = store_data("street_address")
        store_external_number = store_data("external_number_address")
        store_suburb_address = store_data.get("suburb_address")
        store_city_address = store_data.get("city_address")
        store_country_address = store_data.get("country_address")
        store_zippostal_code = store_data.get("zip_postal_code_address")
        store_min_inventory = store_data.get("minimum_inventory")

        store_obj = StoreModel(store_code, store_name, store_external_number, store_street_address, store_suburb_address,
                               store_city_address, store_country_address, store_zippostal_code, store_min_inventory)

        store_data = store_model_db.manage_store_data(store_obj)

        store_data_manage = json.loads(store_data)

        if len(store_data_manage) != 0:
            logger.info('Response Store Data: %s', str(store_data_manage))

            return store_data_manage

    except SQLAlchemyError as error:
        raise mvc_exc.ConnectionError(
            'Can\'t connect to database, verify data connection to "{}".\nOriginal Exception raised: {}'.format(
                store_model_db.__tablename__, error
            )
        )


def get_stores_by_code(store_code):

    store_list_data = {}

    store_get_list_data = select_by_store_code(store_code)

    store_list_data = json.loads(store_get_list_data)

    if store_list_data:

        logger.info('List Stores data by code: {}: {}: '.format(store_code, store_list_data))

        return store_list_data


def update_store_data_endpoint(store_dict_input):
    store_updated = dict()

    store_updated = update_store_data(store_dict_input)

    return store_updated


@app.route('/api/ecommerce/manage/store/', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
@jwt_required
def endpoint_processing_store_data():

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return request_unauthorized()
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        elif request.method == 'POST':

            data = request.get_json(force=True)

            if not data or str(data) is None:
                return request_conflict()

            logger.info('Data Json Store to Manage on DB: %s', str(data))

            json_store_response = manage_store_requested_data(data)

            return json.dumps(json_store_response)

        elif request.method == 'GET':
            data = request.get_json(force=True)

            store_code = data['store_code']

            json_data = []

            json_data = get_stores_by_code(store_code)

            logger.info('Stores List data by Code: %s', str(json_data))

            if not store_code:
                return request_conflict()

            return json.dumps(json_data)

        elif request.method == 'PUT':

            data_store = request.get_json(force=True)

            store_code = data_store.get("store_code")
            store_name = data_store.get("store_name")

            if not data_store:
                return request_conflict()

            json_data = dict()

            json_data = update_store_data_endpoint(data_store)

            logger.info('Data to update Store: %s',
                        "Store code: {0}, Store name: {1}".format(store_code, store_name))

            logger.info('Store updated Info: %s', str(json_data))

            return json_data

        elif request.method == 'DELETE':
            data = request.get_json(force=True)

            store_code = data['store_code']

            logger.info('Store to Delete: %s', 'Store Code: {}'.format(store_code))

            json_data = []

            if not store_code and not Util.validate_store_code_syntax(store_code):
                return request_conflict()

            json_data = delete_store_data(store_code)

            logger.info('Store deleted: %s', json_data)

            return json.dumps(json_data)

        else:
            return not_found()


def manage_product_requested_data(product_data):

    product_data_manage = []

    product_model_db = ProductModelDb()

    try:

        product_sku = product_data.get("product_sku")
        product_unspc = product_data.get("product_unspc")
        product_brand = product_data.get("product_brand")
        category_id = product_data.get("category_id")
        parent_category_id = product_data.get("parent_category_id")
        product_uom = product_data.get("unit_of_measure")
        product_stock = product_data.get("product_stock")
        store_code = product_data.get("product_store_code")
        product_name = product_data.get("product_name")
        product_title = product_data.get("product_title")
        product_long_description = product_data.get("product_long_description")
        product_photo = product_data.get("product_photo")
        product_price = product_data.get("product_price")
        product_tax = product_data.get("product_tax")
        product_currency = product_data.get("product_currency")
        product_status = product_data.get("product_status")
        product_published = product_data.get("product_published")
        manage_stock = product_data.get("product_manage_stock")
        product_length = product_data.get("product_length")
        product_width = product_data.get("product_width")
        product_height = product_data.get("product_height")
        product_weight = product_data.get("product_weight")

        product_obj = ProductModel(product_sku, product_unspc, product_brand, category_id, parent_category_id,
                                   product_uom, product_stock, store_code, product_name, product_title,
                                   product_long_description, product_photo, product_price, product_tax, product_currency,
                                   product_status, product_published, manage_stock, product_length, product_width,
                                   product_height, product_weight)

        data_product = product_model_db.manage_product_data(product_obj)

        product_data_manage = json.loads(data_product)

        if len(product_data_manage) != 0:
            logger.info('Response Product Data: %s', str(product_data_manage))

            return product_data_manage

    except SQLAlchemyError as error:
        raise mvc_exc.ConnectionError(
            'Can\'t connect to database, verify data connection to "{}".\nOriginal Exception raised: {}'.format(
                product_model_db.__tablename__, error
            )
        )


def get_products_by_sku(product_sku):

    product_list_data = {}

    product_get_list_data = select_by_product_sku(product_sku)

    product_list_data = json.loads(product_get_list_data)

    if product_list_data:

        logger.info('List Product data by SKU: {}: {}: '.format(product_sku, product_list_data))

        return product_list_data


@app.route('/api/ecommerce/manage/product/', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
@jwt_required
def endpoint_processing_product_data():

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return request_unauthorized()
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        elif request.method == 'POST':

            data = request.get_json(force=True)

            if not data or str(data) is None:
                return request_conflict()

            logger.info('Data Json Store to Manage on DB: %s', str(data))

            json_store_response = manage_product_requested_data(data)

            return json.dumps(json_store_response)

        elif request.method == 'GET':
            data = request.get_json(force=True)

            product_sku = data['product_sku']

            json_data = []

            json_data = get_products_by_sku(product_sku)

            logger.info('Product List data by SKU: %s', str(json_data))

            if not product_sku:
                return request_conflict()

            return json.dumps(json_data)

        elif request.method == 'PUT':

            data_store = request.get_json(force=True)

            product_sku = data_store.get('product_sku')
            product_stock = data_store.get('product_stock')
            product_store_code = data_store.get('product_store_code')
            product_name = data_store.get('product_name')

            if not data_store:
                return request_conflict()

            json_data = dict()

            json_data = update_product_data(data_store)

            logger.info('Data to update Product: %s',
                        "Product SKU: {0}, "
                        "Product Name: {1}, "
                        "Product Store Code: {2}, "
                        "Product Stock: {3}".format(product_sku, product_name, product_store_code, product_stock))

            logger.info('Product updated Info: %s', str(json_data))

            return json_data

        elif request.method == 'DELETE':
            data = request.get_json(force=True)

            store_code = data['store_code']
            product_sku = data['product_sku']

            logger.info('Store to Delete: %s', 'Store Code: {}'.format(store_code))

            json_data = []

            if not store_code and not Util.validate_store_code_syntax(store_code):
                return request_conflict()

            json_data = delete_product_data(product_sku, store_code)

            logger.info('Product deleted: %s', json_data)

            return json.dumps(json_data)

        else:
            return not_found()


@app.route('/api/ecommerce/authorization/', methods=['POST', 'OPTIONS'])
def get_authentication():

    json_token = {}

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000,
            'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
        }
        return '', 200, headers

    elif request.method == 'POST':
        data = request.get_json(force=True)

        user_name = data['username']
        password = data['password']
        rfc = data['rfc_client']

        regex_email = r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$"

        regex_passwd = r"^[(A-Za-z0-9\_\-\.\$\#\&\*)(A-Za-z0-9\_\-\.\$\#\&\*)]+"

        regex_rfc = r"^([A-ZÑ&]{3,4})?(?:-?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))?(?:-?)?([A-Z\d]{2})([A\d])$"

        match_email = re.match(regex_email, user_name, re.M | re.I)

        match_passwd = re.match(regex_passwd, password, re.M | re.I)

        match_rfc = re.match(regex_rfc, rfc, re.M | re.I)

        if match_email and match_rfc and match_passwd:

            password = password + '_' + rfc

            json_token = user_registration(user_name, password)

            json_token = json.dumps(json_token)

            return json_token

        else:
            return request_conflict()
    else:
        return not_found()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'error_code': 404,
        'error_message': 'Page Not Found: ' + request.url,
    }

    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.errorhandler(500)
def server_error(error=None):
    message = {
        'error_code': 500,
        'error_message': 'Server Error: ' + request.url,
    }

    resp = jsonify(message)
    resp.status_code = 500

    return resp


@app.errorhandler(401)
def request_unauthorized(error=None):
    message = {
        'error_code': 401,
        'error_message': 'Request Unauthorized: ' + request.url,
    }

    resp = jsonify(message)
    resp.status_code = 401

    return resp


@app.errorhandler(409)
def request_conflict(error=None):
    message = {
        "error_code": 409,
        "error_message": 'Request data conflict or Authentication data conflict, please verify it. ' + request.url,
    }

    resp = jsonify(message)
    resp.status_code = 409

    return resp


if __name__ == "__main__":
    app.debug = True

    app.run()

