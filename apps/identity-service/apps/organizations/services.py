from __future__ import annotations

from django.db import transaction

from .models import Company, Membership


@transaction.atomic
def create_company(*, name: str, company_type: str, parent: Company | None = None, is_active: bool = True) -> Company:
    company = Company(name=name, company_type=company_type, parent=parent, is_active=is_active)
    company.full_clean()
    company.save()
    return company


@transaction.atomic
def create_membership(*, user, company: Company, role: str, is_active: bool = True) -> Membership:
    membership = Membership(user=user, company=company, role=role, is_active=is_active)
    membership.full_clean()
    membership.save()
    return membership
