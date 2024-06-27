from django.test import TestCase
from django.core import mail
from unittest.mock import Mock, patch
from todo_list_app.utils import (
    send_reminder_email, local_to_utc, generate_otp, send_code_to_user, verify_otp_code
)
import pytz
from datetime import datetime


class UtilsTestCase(TestCase):

    def test_send_reminder_email(self):
        reminder = Mock()
        reminder.task.title = "Test Task"
        reminder.user.username = "testuser"
        reminder.user.email = "testuser@example.com"

        send_reminder_email(reminder)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reminder: Test Task')
        self.assertIn('Hi testuser', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['testuser@example.com'])

    def test_local_to_utc(self):
        reminder = Mock()
        reminder.remind_at = '2023-06-26T15:00'
        user_timezone = 'Asia/Karachi'

        local_to_utc(user_timezone, reminder)

        utc_time = pytz.utc.localize(datetime(2023, 6, 26, 10, 0))
        self.assertEqual(reminder.remind_at, utc_time)

    def test_generate_otp(self):
        otp = generate_otp()
        self.assertTrue(100000 <= otp <= 999999)

    @patch('todo_list_app.utils.send_email_task.delay')
    @patch('redis.StrictRedis.from_url')
    @patch('todo_list_app.utils.generate_otp')
    def test_send_code_to_user(self, mock_generate_otp, mock_redis_from_url, mock_send_email_task):
        mock_generate_otp.return_value = 123456
        mock_redis_client = Mock()
        mock_redis_from_url.return_value = mock_redis_client

        send_code_to_user('testuser@example.com', 1)

        mock_redis_client.set.assert_called_once_with('ev-1', '123456', ex=120)
        mock_send_email_task.assert_called_once()

    @patch('redis.StrictRedis.from_url')
    def test_verify_otp_code(self, mock_redis_from_url):
        mock_redis_client = Mock()
        mock_redis_from_url.return_value = mock_redis_client
        mock_redis_client.get.return_value = b'123456'

        result = verify_otp_code('123456', 1)

        self.assertTrue(result)
        mock_redis_client.delete.assert_called_once_with('ev-1')

        result = verify_otp_code('654321', 1)

        self.assertFalse(result)

