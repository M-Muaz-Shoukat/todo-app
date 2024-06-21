
from django.test import TestCase
from todo_list_app.models import Category, User, Task, Reminder
from datetime import datetime, timezone


class ReminderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='testpassword',
                                             first_name='Test', last_name='Name')
        self.client.login(email='test@gmail.com', password='testpassword')
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.task = Task.objects.create(title="Title", description="Title to Test", due_date="2024-06-20",
                                          completed=False, category=self.category)
        self.object = Reminder.objects.create(user=self.user, task=self.task, remind_at='2025-05-12T16:21:00Z',
                                              is_sent=False)

    def test_reminder_creation(self):
        self.assertEqual(self.object.remind_at, "2025-05-12T16:21:00Z")

    def test_reminder_list(self):
        objects = Reminder.objects.all()
        expected_remind_at = datetime.fromisoformat("2025-05-12T16:21:00+00:00").replace(tzinfo=timezone.utc)
        self.assertEqual(objects[0].remind_at, expected_remind_at)

    def test_reminder_update(self):
        obj = Reminder.objects.get(id=self.object.id)
        obj.remind_at = datetime.fromisoformat("2024-02-01T22:22:00+00:00").replace(tzinfo=timezone.utc)
        obj.save()
        obj = Reminder.objects.get(id=self.object.id)
        self.assertEqual(obj.remind_at,
                         datetime.fromisoformat("2024-02-01T22:22:00+00:00").replace(tzinfo=timezone.utc))

    def test_reminder_delete(self):
        obj = Reminder.objects.get(id=self.object.id)
        expected_remind_at = datetime.fromisoformat("2025-05-12T16:21:00+00:00").replace(tzinfo=timezone.utc)
        self.assertEqual(obj.remind_at, expected_remind_at)
        obj.delete()
        self.assertFalse(Task.objects.filter(reminder__remind_at=expected_remind_at).exists())

    def test_task_sent_false_constraint(self):
        obj = Reminder.objects.create(user=self.user, task=self.task, remind_at='2024-04-12T16:21:00Z')
        self.assertEqual(obj.is_sent, False)

