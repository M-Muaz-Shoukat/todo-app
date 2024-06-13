
import json
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

User = get_user_model()


class TestTaskAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="muazdev01@gmail.com", password="admin123456789", first_name="Muaz",
                                             last_name="Shouakt")
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        category = self.client.post('/todo/categories', {"name": "Work"}, format='json')
        self.category = json.loads(category.content)
        response = self.client.post('/todo/tasks', {"title": "title here is now!",
                                                    "description": "description", "due_date": "2024-06-20",
                                                    "completed": False, "category": self.category['id'],
                                                    "reminder": {"remind_at": "2025-05-12 16:21"}}, format='json')
        content_list = json.loads(response.content)
        self.object = content_list

    def test_tasks_get_endpoint(self):
        response = self.client.get('/todo/tasks')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_post_endpoint(self):
        response = self.client.post('/todo/tasks', {"title": "title here is now!",
                                                    "description": "description", "due_date": "2024-06-20",
                                                    "completed": False, "category": self.category['id'],
                                                    "reminder": {"remind_at": "2025-05-12 16:21"}},format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_task_patch_endpoint(self):
        response = self.client.patch(f'/todo/tasks/{self.object['id']}', {"title": "No title here"},format='json')
        content = json.loads(response.content)
        self.assertEqual(content['title'], "No title here")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_delete_endpoint(self):
        response = self.client.delete(f'/todo/tasks/{self.object['id']}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_retrieve_endpoint(self):
        response = self.client.get(f'/todo/tasks/{self.object['id']}')
        content = json.loads(response.content)
        self.assertEqual(content['title'], "title here is now!")



