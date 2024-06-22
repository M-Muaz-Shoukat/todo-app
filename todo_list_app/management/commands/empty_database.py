from django.core.management.base import BaseCommand
from todo_list_app.models import Task, User, Category, Reminder


class Command(BaseCommand):
    help = 'Empty the database'

    def handle(self, *args, **options):
        try:
            User.objects.all().delete()
            Category.objects.all().delete()
            Task.objects.all().delete()
            Reminder.objects.all().delete()
        except Exception as e:
            print(f'Error: {e}')

