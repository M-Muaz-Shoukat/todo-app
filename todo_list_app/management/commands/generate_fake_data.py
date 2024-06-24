from django.core.management.base import BaseCommand
from todo_list_app.models import Reminder, User, Task, Category
from faker import Faker
import requests, random

fake = Faker()


class Command(BaseCommand):
    help = 'Generate fake data'

    def add_arguments(self, parser):
        parser.add_argument('user_count', type=int, help='Number of User records to generate')
        parser.add_argument('category_count', type=int, help='Number of category records to generate')
        parser.add_argument('task_count', type=int, help='Number of task records to generate')

    def handle(self, *args, **options):
        user_count = options['user_count']
        category_count = options['category_count']
        task_count = options['task_count']
        for i in range(user_count):
            data = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'password': 'admin123456789',
                'password2': 'admin123456789',
            }
            try:
                response = requests.post('http://127.0.0.1:8000/auth/register', json=data)
                response.raise_for_status()
                print(f'Record {i+1} successfully added')
            except requests.exceptions.RequestException as e:
                print(f"Error registering user record {i+1}: {e}")

            user = User.objects.get(email=data['email'])
            for j in range(category_count):
                category = Category.objects.create(user=user, name=fake.word())
                for k in range(task_count):
                    task = Task.objects.create(
                        category=category,
                        title=fake.catch_phrase() + f" ({category.name})",
                        description=fake.sentence(nb_words=5),
                        due_date=fake.date(),
                        completed=random.choices([True, False], weights=[0.8, 0.2])[0],
                        reminder=None
                    )

                    if random.choices([True, False], weights=[0.3, 0.7])[0]:
                        task.reminder = Reminder.objects.create(user=user, task=task, remind_at=fake.date_time())
                        task.save()



