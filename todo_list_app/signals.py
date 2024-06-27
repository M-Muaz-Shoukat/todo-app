from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from todo_list_app.utils import send_email_invite_to_assignee


@receiver(post_save, sender=Task)
def send_email_to_assignee(sender, instance, created, **kwargs):
    if created:
        send_email_invite_to_assignee(instance)


