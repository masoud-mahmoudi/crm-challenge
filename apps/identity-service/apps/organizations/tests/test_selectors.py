from django.test import TestCase

from apps.accounts.services import create_user
from apps.organizations.models import Company, Membership
from apps.organizations.selectors import list_accessible_companies_for_user
from apps.organizations.services import create_company, create_membership


class AccessibleCompanySelectorTests(TestCase):
    def test_parent_user_sees_descendant_child_companies_only(self):
        parent = create_company(name="Acme Group", company_type=Company.CompanyType.PARENT)
        toronto = create_company(name="Acme Toronto", company_type=Company.CompanyType.CHILD, parent=parent)
        montreal = create_company(name="Acme Montreal", company_type=Company.CompanyType.CHILD, parent=parent)
        other_parent = create_company(name="Other Group", company_type=Company.CompanyType.PARENT)
        create_company(name="Other Child", company_type=Company.CompanyType.CHILD, parent=other_parent)

        user = create_user(email="parent@example.com", password="password123", full_name="Parent User")
        create_membership(user=user, company=parent, role=Membership.Role.PARENT_ADMIN)

        companies = list(list_accessible_companies_for_user(user))

        self.assertEqual({company.name for company in companies}, {parent.name, toronto.name, montreal.name})
