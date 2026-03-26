from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.services import create_user
from apps.authn.services import issue_access_token
from apps.organizations.models import Company, Membership
from apps.organizations.services import create_company, create_membership


class MeViewTests(APITestCase):
    def test_me_endpoint_requires_authentication_and_returns_memberships(self):
        company = create_company(name="Acme Group", company_type=Company.CompanyType.PARENT)
        user = create_user(email="me@example.com", password="password123", full_name="Me User")
        create_membership(user=user, company=company, role=Membership.Role.PARENT_MANAGER)

        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {issue_access_token(user)}"
        response = self.client.get(reverse("me"))
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["email"], "me@example.com")
        self.assertEqual(len(payload["memberships"]), 1)
