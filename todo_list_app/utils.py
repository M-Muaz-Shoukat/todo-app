# utils.py
import pytz
import random
from datetime import datetime
from todo_list_app.models import Task
from django.core.mail import send_mail
from django.conf import settings
from todo_list import settings
from django.core.mail import EmailMessage
from todo_list_app.models import User, OneTimePassword


def send_reminder_email(reminder):
    subject = f'Reminder: {reminder.task.title}'
    message = f'Hi {reminder.user.username},\n\nThis is a reminder for your task: {reminder.task.title}.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reminder.user.email])


def local_to_utc(user_timezone, reminder):
    if user_timezone:
        user_tz = pytz.timezone(user_timezone)
    else:
        user_tz = pytz.utc
    remind_at = datetime.strptime(reminder.remind_at, '%Y-%m-%dT%H:%M')
    localized_remind_at = user_tz.localize(remind_at, is_dst=None)
    reminder.remind_at = localized_remind_at.astimezone(pytz.utc)


def reminder_create_or_update(user, reminder, timezone, task_id):
    local_to_utc(timezone, reminder)
    reminder.user = user
    reminder.task = Task.objects.get(id=task_id)
    return reminder.save()


def generate_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp


def send_code_to_user(email):
    subject = "One Time Passcode for Email Verification"
    otp_code = generate_otp()
    print(otp_code)
    user = User.objects.get(email=email)
    current_site = "myAuth.com"
    email_body = f"Hi thanks for signing up on {current_site}. Please verify your email with the \n one time passcode {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    OneTimePassword.objects.create(user=user, code=otp_code)
    d_email = EmailMessage(subject, email_body, from_email, [email])
    d_email.send(fail_silently=True)


def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[data['to_email']]
    )
    email.send(fail_silently=True)
