from django.test import TestCase
from todo_list_app.models import User
from django.db.utils import DataError, IntegrityError


class UserTestCase(TestCase):
    def setUp(self):
        self.object = User.objects.create_user(email='test@gmail.com', password='testpassword',
                                               first_name='Test', last_name='Name')

    def test_user_creation(self):
        self.assertEqual(self.object.email, "test@gmail.com")

    def test_user_list(self):
        objects = User.objects.all()
        self.assertEqual(objects[0].email, "test@gmail.com")

    def test_user_update(self):
        obj = User.objects.get(id=self.object.id)
        obj.first_name = "New Test"
        obj.save()
        obj = User.objects.get(id=self.object.id)
        self.assertEqual(obj.first_name, "New Test")

    def test_user_delete(self):
        obj = User.objects.get(id=self.object.id)
        self.assertEqual(obj.first_name, "Test")
        obj.delete()
        self.assertFalse(User.objects.filter(first_name="Test").exists())

    def test_user_name_length_constraint(self):
        first_name = ("In today's rapidly evolving tech landscape, innovation "
                      "permeates every facet of our lives. Artificial intelligence")
        last_name = ("is streamlining daily tasks, while advancements in "
                     "sustainable technologies are reshaping industries. "
                     "Across the globe, companies are investing heavily in ")

        with self.assertRaises(DataError):
            User.objects.create(email='test2@gmail.com', password='testpassword',
                                first_name=first_name, last_name=last_name)

    def test_user_email_unique_contraint(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(email='test@gmail.com', password='testpassword',
                                first_name='abc', last_name='nwe')