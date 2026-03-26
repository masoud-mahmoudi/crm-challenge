from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_create_user_with_email_as_username(self):
        user = User.objects.create_user(
            email="USER@EXAMPLE.COM",
            password="password123",
            full_name="Example User",
        )

        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.full_name, "Example User")
