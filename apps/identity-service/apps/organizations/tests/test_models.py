from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.services import create_user
from apps.organizations.models import Company, Membership
from apps.organizations.services import create_company


class CompanyValidationTests(TestCase):
    def test_child_company_requires_parent(self):
        with self.assertRaises(ValidationError):
            create_company(name="Acme Child", company_type=Company.CompanyType.CHILD)


class MembershipValidationTests(TestCase):
    def test_parent_role_cannot_be_assigned_to_child_company(self):
        parent = create_company(name="Acme Group", company_type=Company.CompanyType.PARENT)
        child = create_company(name="Acme Toronto", company_type=Company.CompanyType.CHILD, parent=parent)
        user = create_user(email="member@example.com", password="password123", full_name="Member User")
        membership = Membership(user=user, company=child, role=Membership.Role.PARENT_ADMIN)

        with self.assertRaises(ValidationError):
            membership.full_clean()
