import json
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

User = get_user_model()


class TestCategoryAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="muazdev01@gmail.com", password="admin123456789", first_name="Muaz", last_name="Shouakt")
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+access_token)

    def _create_category(self):
        response = self.client.post('/todo/categories', {"name": "Work"}, format='json')
        content_list = json.loads(response.content)
        self.object = content_list

    def test_category_get_endpoint(self):
        self._create_category()
        response = self.client.get('/todo/categories')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_post_endpoint(self):
        self._create_category()
        response = self.client.post('/todo/categories', {"name": "New HomeWork"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_category_patch_endpoint(self):
        self._create_category()
        response = self.client.patch(f'/todo/categories/{self.object['id']}', {"name": "Some what Personal"})
        content = json.loads(response.content)
        self.assertEqual(content['name'],"Some what Personal")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_delete_endpoint(self):
        self._create_category()
        response = self.client.delete(f'/todo/categories/{self.object['id']}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_category_retrieve_endpoint(self):
        self._create_category()
        response = self.client.get(f'/todo/categories/{self.object['id']}')
        content = json.loads(response.content)
        self.assertEqual(content['name'],"Work")



