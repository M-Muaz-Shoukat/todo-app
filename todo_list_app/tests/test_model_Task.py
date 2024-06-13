
from django.test import TestCase
from todo_list_app.models import Category, User, Task
from django.db.utils import DataError


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='testpassword',
                                             first_name='Test', last_name='Name')
        self.client.login(email='test@gmail.com', password='testpassword')
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.object = Task.objects.create(title="Title", description="Title to Test", due_date="2024-06-20",
                                          completed=False, category=self.category)

    def test_task_creation(self):
        self.assertEqual(self.object.title, "Title")

    def test_task_list(self):
        objects = Task.objects.all()
        self.assertEqual(objects[0].title, "Title")

    def test_task_update(self):
        obj = Task.objects.get(id=self.object.id)
        obj.title = "New Test Title"
        obj.save()
        obj = Task.objects.get(id=self.object.id)
        self.assertEqual(obj.title, "New Test Title")

    def test_task_delete(self):
        obj = Task.objects.get(id=self.object.id)
        self.assertEqual(obj.title, "Title")
        obj.delete()
        self.assertFalse(Task.objects.filter(title="Title").exists())

    def test_task_name_length_constraint(self):
        long_title = ("In today's rapidly evolving tech landscape, innovation "
                     "permeates every facet of our lives. Artificial intelligence"
                     " is streamlining daily tasks, while advancements in "
                     "sustainable technologies are reshaping industries. "
                     "Across the globe, companies are investing heavily in "
                     "research and development to pioneer groundbreaking "
                     "solutions.")

        with self.assertRaises(DataError):
            Task.objects.create(title=long_title,description="Title to Test", due_date="2024-06-20",
                                completed=False, category=self.category)

    def test_task_null_description_constraint(self):
        obj = Task.objects.create(title="new title", due_date="2024-06-20",
                                  completed=False, category=self.category)
        self.assertEqual(obj.description, None)

    def test_task_completed_false_constraint(self):
        obj = Task.objects.create(title="new title", due_date="2024-06-20",category=self.category)
        self.assertEqual(obj.completed, False)

