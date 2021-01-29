# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A25.1 ($Rev: 1 $)"

import unittest
import json
from tests.BaseCase import BaseCase


class TestManageInvStock(BaseCase):

    def get_token_auth_api(self):
        username = "jorge.morfinez.m@gmail.com"
        password = "Jm$_#11388"
        rfc_client = "MOMJ880813RQ7"

        auth_payload = json.dumps({
            "username": username,
            "password": password,
            "rfc_client": rfc_client,
        })

        header_auth = {"Content-Type": "application/json"}

        response_token = self.app.post('/api/ecommerce/authorization/', headers=header_auth,
                                       data=auth_payload)

        token_response = json.loads(response_token.get_data(as_text=True))

        token_api_auth = token_response['access_token']

        return token_api_auth

    def stock_list_total(self):

        product_sku_param = "A20981"
        stock_list_payload = {
            "product_sku": product_sku_param
        }

        token_api_auth = self.get_token_auth_api()

        header_request = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token_api_auth}"
        }

        response_stock = self.app.get('/api/ecommerce/stock/total/',
                                      headers=header_request,
                                      data=json.dumps(stock_list_payload))

        # When
        list_stock_response = json.loads(response_stock.get_data(as_text=True))

        print("Response endpoint: ", list_stock_response)

        # Then
        # "SKU": sku_product,
        # "ProductStock": {
        #     "CodeStore": code_store,
        #     "NameStore": name_store,
        #     "Stock": stock_product,
        # }
        # self.assertEqual(movie_payload['name'], added_movie['name'])
        # self.assertEqual(movie_payload['casts'], added_movie['casts'])
        # self.assertEqual(movie_payload['genres'], added_movie['genres'])
        # self.assertEqual(user_id, added_movie['added_by']['$oid'])
        self.assertEqual(200, response_stock.status_code)
        self.assertEqual(str, type(list_stock_response["SKU"]))
        self.assertEqual(str, type(list_stock_response["ProductStock"]["CodeStore"]))
        self.assertEqual(str, type(list_stock_response["ProductStock"]["NameStore"]))
        self.assertEqual(str, type(list_stock_response["ProductStock"]["Stock"]))

    # def test_empty_response(self):
    #
    #     response = self.app.get('/api/ecommerce/stock/total/')
    #
    #     api_response = json.loads(response.get_data(as_text=True))
    #
    #     self.assertEqual(str, type(api_response['message']))
    #     # self.assertEqual(str, type(api_response['code']))
    #     self.assertNotEqual(200, response.status_code)
