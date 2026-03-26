from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.services import create_user
from apps.organizations.models import Company, Membership
from apps.organizations.services import create_company, create_membership


class AuthApiTests(APITestCase):
    def setUp(self):
        self.user = create_user(
            email="parent.admin@acme.com",
            password="password123",
            full_name="Parent Admin",
            is_staff=True,
        )
        company = create_company(name="Acme Group", company_type=Company.CompanyType.PARENT)
        create_membership(user=self.user, company=company, role=Membership.Role.PARENT_ADMIN)

    def test_login_endpoint_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            reverse("login"),
            {"email": "parent.admin@acme.com", "password": "password123"},
            format="json",
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", payload)
        self.assertIn("refresh_token", payload)
