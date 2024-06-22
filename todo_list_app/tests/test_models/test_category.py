from django.test import TestCase
from todo_list_app.models import Category, User
from django.db.utils import DataError


class CategoryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='testpassword',
                                             first_name='Test', last_name='Name')
        self.client.login(email='test@gmail.com', password='testpassword')
        self.object = Category.objects.create(user=self.user, name="Test Category")

    def test_category_creation(self):
        self.assertEqual(self.object.name, "Test Category")

    def test_category_list(self):
        objects = Category.objects.all()
        self.assertEqual(objects[0].name, "Test Category")

    def test_category_update(self):
        obj = Category.objects.get(id=self.object.id)
        obj.name = "New Test Category"
        obj.save()
        obj = Category.objects.get(id=self.object.id)
        self.assertEqual(obj.name, "New Test Category")

    def test_category_delete(self):
        obj = Category.objects.get(id = self.object.id)
        self.assertEqual(obj.name, "Test Category")
        obj.delete()
        self.assertFalse(Category.objects.filter(name="Test Category").exists())

    def test_category_name_length_constraint(self):
        long_name = ("In today's rapidly evolving tech landscape, innovation "
                     "permeates every facet of our lives. Artificial intelligence"
                     " is streamlining daily tasks, while advancements in "
                     "sustainable technologies are reshaping industries. "
                     "Across the globe, companies are investing heavily in "
                     "research and development to pioneer groundbreaking "
                     "solutions.")

        with self.assertRaises(DataError):
            Category.objects.create(user=self.user, name=long_name)

