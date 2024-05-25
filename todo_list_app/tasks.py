from celery import shared_task
from django.utils import timezone
from todo_list_app.models import Reminder
from .utils import send_reminder_email


@shared_task
def check_and_send_reminders():
    now = timezone.now()
    reminders = Reminder.objects.filter(remind_at__lte=now, is_sent=False)
    for reminder in reminders:
        send_reminder_email(reminder)
        reminder.is_sent = True
        reminder.save()

    return str(reminders)

