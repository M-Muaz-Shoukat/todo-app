from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserManagerTestCase(TestCase):

    def setUp(self):
        self.user_manager = User.objects

    def test_email_validator_valid_email(self):
        valid_email = "testuser@example.com"
        try:
            self.user_manager.email_validator(valid_email)
        except ValueError:
            self.fail("In Valid Email")

    def test_create_user_no_first_name(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_user("testuser@example.com", None, "User", "password123")

    def test_create_user_success(self):
        email = "testuser@example.com"
        first_name = "Test"
        last_name = "User"
        password = "password123"
        user = self.user_manager.create_user(email, first_name, last_name, password)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_success(self):
        email = "superuser@example.com"
        first_name = "Super"
        last_name = "User"
        password = "password123"
        user = self.user_manager.create_superuser(email, first_name, last_name, password)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_verified)

