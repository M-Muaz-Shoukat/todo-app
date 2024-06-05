# utils.py
import pytz
import redis
import random
from datetime import datetime
from todo_list_app.models import Task
from django.core.mail import send_mail
from django.conf import settings
from todo_list import settings
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str


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
    otp = random.randint(100000, 999999)
    return otp


redis_client = redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])


def send_code_to_user(email, user_id):
    subject = "One Time Passcode for Email Verification"
    otp_code = generate_otp()
    key = str(otp_code)
    while redis_client.get(key) is not None:
        otp_code = generate_otp()
        key = str(otp_code)
    redis_client.set(key, urlsafe_base64_encode(smart_bytes(user_id)), ex=120)
    print(otp_code)
    current_site = "TodoList.com"
    email_body = f"Hi thanks for signing up on {current_site}. Please verify your email with the \n one time passcode {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    d_email = EmailMessage(subject, email_body, from_email, [email])
    d_email.send(fail_silently=True)


def verify_otp_code(otp_entered):
    key = otp_entered
    user_id = redis_client.get(key)

    if user_id is not None:
        redis_client.delete(key)

    return user_id


def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[data['to_email']]
    )
    email.send(fail_silently=True)
