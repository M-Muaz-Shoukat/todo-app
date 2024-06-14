
import json
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

User = get_user_model()


class TestAuthAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        response = self.client.post('/auth/register', {"email": "muazdev03@gmail.com", "first_name": "Zaim",
                                                                "last_name": "Rana", "password": "admin123456789",
                                                                "password2": "admin123456789"}, format='json')
        self.object = json.loads(response.content)
        user = User.objects.get(email=self.object['data']['email'])
        user.is_verified = True
        user.save()

    def test_auth_register_endpoint(self):
        self.assertEqual(self.object['data']['email'], "muazdev03@gmail.com")

    def test_auth_login_endpoint(self):
        response = self.client.post('/auth/login', {"email": "muazdev03@gmail.com",
                                                    "password": "admin123456789"}, format='json')
        user = json.loads(response.content)
        self.assertEqual(user['email'], "muazdev03@gmail.com")

    def test_auth_logout_endpoint(self):
        response = self.client.post('/auth/login', {"email": "muazdev03@gmail.com",
                                                    "password": "admin123456789"}, format='json')
        user = json.loads(response.content)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user['access_token'])
        response = self.client.post('/auth/logout', {"refresh_token": user['access_token']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)




