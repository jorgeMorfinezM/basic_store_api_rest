import unittest
import json
from tests.BaseCase import BaseCase


class TestManageStock(BaseCase):
    def test_empty_response(self):

        response = self.app.get('/api/ecommerce/stock/total/')
        self.assertListEqual(response.json, [])
        self.assertEqual(response.status_code, 200)

    def stock_list_total(self):
        username = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc_client = "RFC_WITH_OMOCLAVE"

        auth_payload = json.dumps({
            "username": username,
            "password": password,
            "rfc_client": rfc_client,
        })

        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=auth_payload)

        token_api_auth = response.json['access_token']

        product_sku_param = "A20981"
        stock_list_payload = {
            "product_sku": product_sku_param
        }

        response = self.app.get('/api/ecommerce/stock/total/',
                                headers={"Content-Type": "application/json", "Authorization": f"Bearer {login_token}"},
                                data=json.dumps(stock_list_payload))

        # When
        response = self.app.get('/api/movies')
        added_movie = response.json[0]

        # Then
        "SKU": sku_product,
        "ProductStock": {
            "CodeStore": code_store,
            "NameStore": name_store,
            "Stock": stock_product,
        }
        self.assertEqual(movie_payload['name'], added_movie['name'])
        self.assertEqual(movie_payload['casts'], added_movie['casts'])
        self.assertEqual(movie_payload['genres'], added_movie['genres'])
        self.assertEqual(user_id, added_movie['added_by']['$oid'])
        self.assertEqual(200, response.status_code)
