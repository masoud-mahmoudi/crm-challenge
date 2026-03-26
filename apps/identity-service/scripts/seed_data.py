import os
import sys
from pathlib import Path

import django


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.chdir(BASE_DIR)
django.setup()

from apps.accounts.services import get_or_create_user  # noqa: E402
from apps.organizations.models import Company, Membership  # noqa: E402
from apps.organizations.services import create_company, create_membership  # noqa: E402


def get_or_create_company(*, name: str, company_type: str, parent=None):
    company = Company.objects.filter(name=name).first()
    if company:
        company.company_type = company_type
        company.parent = parent
        company.is_active = True
        company.save()
        return company
    return create_company(name=name, company_type=company_type, parent=parent)


def get_or_create_membership(*, user, company, role: str):
    membership = Membership.objects.filter(user=user, company=company, role=role).first()
    if membership:
        membership.is_active = True
        membership.save(update_fields=["is_active", "updated_at"])
        return membership
    return create_membership(user=user, company=company, role=role)


def seed() -> None:
    aerialytic_group = get_or_create_company(name="Aerialytic Group", company_type=Company.CompanyType.PARENT)
    aerialytic_toronto = get_or_create_company(
        name="Aerialytic Toronto",
        company_type=Company.CompanyType.CHILD,
        parent=aerialytic_group,
    )
    aerialytic_montreal = get_or_create_company(
        name="Aerialytic Montreal",
        company_type=Company.CompanyType.CHILD,
        parent=aerialytic_group,
    )

    parent_admin = get_or_create_user(
        email="parent.admin@aerialytic.com",
        password="password123",
        full_name="Parent Admin",
        is_staff=True,
    )
    toronto_rep = get_or_create_user(
        email="toronto.rep@aerialytic.com",
        password="password123",
        full_name="Toronto Rep",
    )
    montreal_rep = get_or_create_user(
        email="montreal.rep@aerialytic.com",
        password="password123",
        full_name="Montreal Rep",
    )

    get_or_create_membership(user=parent_admin, company=aerialytic_group, role=Membership.Role.PARENT_ADMIN)
    get_or_create_membership(user=toronto_rep, company=aerialytic_toronto, role=Membership.Role.SALES_REP)
    get_or_create_membership(user=montreal_rep, company=aerialytic_montreal, role=Membership.Role.SALES_REP)

    # the second entities for testing the isolation of the child companies and leads
    masoud_group = get_or_create_company(name="Masoud Group", company_type=Company.CompanyType.PARENT)
    masoud_toronto = get_or_create_company(
        name="Masoud Toronto",
        company_type=Company.CompanyType.CHILD,
        parent=masoud_group,
    )
    masoud_montreal = get_or_create_company(
        name="Masoud Montreal",
        company_type=Company.CompanyType.CHILD,
        parent=masoud_group,
    )

    parent_admin = get_or_create_user(
        email="parent.admin@masoud.com",
        password="password123",
        full_name="Parent Admin",
        is_staff=True,
    )
    toronto_rep = get_or_create_user(
        email="toronto.rep@masoud.com",
        password="password123",
        full_name="Toronto Rep",
    )
    montreal_rep = get_or_create_user(
        email="montreal.rep@masoud.com",
        password="password123",
        full_name="Montreal Rep",
    )

    get_or_create_membership(user=parent_admin, company=masoud_group, role=Membership.Role.PARENT_ADMIN)
    get_or_create_membership(user=toronto_rep, company=masoud_toronto, role=Membership.Role.SALES_REP)
    get_or_create_membership(user=montreal_rep, company=masoud_montreal, role=Membership.Role.SALES_REP)


if __name__ == "__main__":
    seed()
    print("Seed data created.")
