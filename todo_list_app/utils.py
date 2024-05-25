# utils.py
from django.core.mail import send_mail
from django.conf import settings


def send_reminder_email(reminder):
    subject = f'Reminder: {reminder.task.title}'
    message = f'Hi {reminder.user.username},\n\nThis is a reminder for your task: {reminder.task.title}.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reminder.user.email])