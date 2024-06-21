import json
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from unittest.mock import patch

User = get_user_model()


class TestAuthAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "muazdev01@gmail.com",
            "first_name": "Zaim",
            "last_name": "Rana",
            "password": "admin123456789",
            "password2": "admin123456789"
        }

    def _register_user(self):
        response = self.client.post('/auth/register', self.user_data, format='json')
        user_data = json.loads(response.content)
        return user_data

    def _verify_user(self, user_data):
        response = self.client.post('/auth/verify-email', {'code': '123456',
                                                           'user_id': f'{user_data["user_id"]}'},
                                    format='json')
        return response

    def test_auth_register_endpoint(self):
        user_data = self._register_user()
        self.assertEqual(user_data['data']['email'], self.user_data['email'])

    @patch('todo_list_app.utils.generate_otp')
    def test_auth_verify_email_endpoint(self, mock_generate_otp):
        mock_generate_otp.return_value = '123456'
        user_data = self._register_user()
        response = self._verify_user(user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('todo_list_app.utils.generate_otp')
    def test_auth_login_endpoint(self, mock_generate_otp):
        mock_generate_otp.return_value = '123456'
        user_data = self._register_user()
        self._verify_user(user_data)
        response = self.client.post('/auth/login', {"email": self.user_data['email'],
                                                    "password": self.user_data['password']}, format='json')
        user = json.loads(response.content)
        self.assertEqual(user['email'], self.user_data['email'])

    @patch('todo_list_app.utils.generate_otp')
    def test_auth_logout_endpoint(self,mock_generate_otp):
        mock_generate_otp.return_value = '123456'
        user_data = self._register_user()
        self._verify_user(user_data)
        response = self.client.post('/auth/login', {"email": self.user_data['email'],
                                                    "password": self.user_data['password']}, format='json')
        user = json.loads(response.content)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user['access_token'])
        response = self.client.post('/auth/logout', {"refresh_token": user['refresh_token']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

