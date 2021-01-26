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
from tests.BaseCase import BaseCase


class TestUserLogin(BaseCase):

    def test_successful_login(self):

        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['message']))
        self.assertEqual(str, type(response.json['access_token']))
        self.assertEqual(str, type(response.json['refresh_token']))
        self.assertEqual(200, response.status_code)

    def test_login_with_invalid_username(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        payload['username'] = "jorgemorfinez_gmail.com"
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_with_invalid_password(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        payload['password'] = "123"
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_with_invalid_rfc_client(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        payload['password'] = "MOMJ"
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_with_non_existing_field(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
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

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_without_username(self):
        password = "Jm$_&1388"
        rfc = "MOMJ880813"

        payload = json.dumps({
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_without_password(self):
        user_name = "jorge.morfinez.m@gmail.com"
        rfc = "MOMJ880813"

        payload = json.dumps({
            "username": user_name,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_without_rfc_client(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"

        payload = json.dumps({
            "username": user_name,
            "password": password,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['error_message']))
        self.assertEqual(int, type(response.json['error_code']))

    def test_login_already_existing_user(self):
        user_name = "jorge.morfinez.m@gmail.com"
        password = "Jm$_&1388"
        rfc = "MOMJ880813"
        payload = json.dumps({
            "username": user_name,
            "password": password,
            "rfc_client": rfc,
        })

        # When
        response = self.app.post('/api/ecommerce/authorization/', headers={"Content-Type": "application/json"},
                                 data=payload)

        # Then
        self.assertEqual(str, type(response.json['message']))
        self.assertEqual(int, response.status_code)

# if __name__ == '__main__':
#     unittest.main()
