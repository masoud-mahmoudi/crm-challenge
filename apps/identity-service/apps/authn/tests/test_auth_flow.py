from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.services import create_user
from apps.authn.services import issue_access_token
from apps.organizations.models import Company, Membership
from apps.organizations.services import create_company, create_membership


class AuthenticatedFlowTests(APITestCase):
    def test_me_endpoint_rejects_missing_token(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 401)

    def test_companies_endpoint_returns_accessible_companies(self):
        parent = create_company(name="Acme Group", company_type=Company.CompanyType.PARENT)
        child = create_company(name="Acme Toronto", company_type=Company.CompanyType.CHILD, parent=parent)
        user = create_user(email="rep@example.com", password="password123", full_name="Sales Rep")
        create_membership(user=user, company=child, role=Membership.Role.SALES_REP)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_access_token(user)}")
        response = self.client.get(reverse("company-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([company["name"] for company in response.data], ["Acme Toronto"])
