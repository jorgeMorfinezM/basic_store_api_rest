# -*- coding: utf-8 -*-
"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021, Jorge Morfinez Mojica"
__license__ = ""
__history__ = """ """
__version__ = "1.1.A25.1 ($Rev: 1 $)"

import json
from tests.BaseCase import BaseCase


class TestUserLogin(BaseCase):

    def test_successful_login(self):

        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))
        # print("JSON Response: ", json.dumps(token_response))

        # Then
        self.assertEqual(str, type(token_response['message']))
        self.assertEqual(str, type(token_response['access_token']))
        self.assertEqual(str, type(token_response['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_login_already_existing_user(self):
        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))
        # print("JSON Response: ", json.dumps(token_response))

        # Then
        self.assertEqual(str, type(token_response['message']))
        self.assertEqual(str, type(token_response['access_token']))
        self.assertEqual(str, type(token_response['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_login_with_invalid_username(self):
        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(token_response['error_message']))
        self.assertEqual(int, type(token_response['error_code']))

    def test_login_with_invalid_password(self):
        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(token_response['error_message']))
        self.assertEqual(int, type(token_response['error_code']))

    def test_login_with_invalid_rfc_client(self):
        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(token_response['error_message']))
        self.assertEqual(int, type(token_response['error_code']))

    def test_login_with_non_existing_field(self):
        user_name = "EMAIL_USING_DOMAIN"
        password = "PASSWORD"
        rfc = "RFC_WITH_HOMOCLAVE"
        
        data = "aeiou12345"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
            "data": data,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        token_response = json.loads(response.get_data(as_text=True))

        # Then
        self.assertEqual(str, type(token_response['error_message']))
        self.assertEqual(int, type(token_response['error_code']))

