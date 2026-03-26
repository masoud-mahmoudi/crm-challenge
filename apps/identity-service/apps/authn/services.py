from __future__ import annotations

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.accounts.services import create_user
from apps.accounts.selectors import get_user_by_id
from apps.accounts.models import User
from apps.organizations.models import Company
from apps.organizations.selectors import list_accessible_companies_for_user, list_memberships_for_user
from infrastructure.auth.jwt_issuer import TokenError, issue_token, verify_token


def build_membership_claims(user: User) -> tuple[list[str], list[dict[str, str | None]]]:
    memberships = list(list_memberships_for_user(user))
    roles = sorted({membership.role for membership in memberships})
    membership_claims = [
        {
            "company_id": str(membership.company.id),
            "company_name": membership.company.name,
            "company_type": membership.company.company_type,
            "parent_company_id": str(membership.company.parent.id) if membership.company.parent else None,
            "role": membership.role,
        }
        for membership in memberships
    ]
    return roles, membership_claims


def build_tenant_access_claims(user: User) -> dict[str, object]:
    memberships = list(list_memberships_for_user(user))
    accessible_companies = list(list_accessible_companies_for_user(user))

    membership_company_ids = sorted({str(membership.company_id) for membership in memberships})
    parent_company_ids = sorted(
        {
            str(membership.company_id)
            for membership in memberships
            if membership.company.company_type == Company.CompanyType.PARENT
        }
    )
    visible_company_ids = sorted({str(company.id) for company in accessible_companies})
    data_company_ids = sorted(
        {
            str(company.id)
            for company in accessible_companies
            if company.company_type == Company.CompanyType.CHILD
        }
    )
    default_company_id = (
        data_company_ids[0]
        if data_company_ids
        else (visible_company_ids[0] if visible_company_ids else None)
    )

    return {
        "membership_company_ids": membership_company_ids,
        "parent_company_ids": parent_company_ids,
        "visible_company_ids": visible_company_ids,
        "data_company_ids": data_company_ids,
        "default_company_id": default_company_id,
    }


def authenticate_user(*, email: str, password: str) -> User:
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if not user or not user.check_password(password):
        raise AuthenticationFailed("Invalid email or password")
    return user


def register_user(*, email: str, password: str, full_name: str) -> User:
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError("A user with this email already exists")
    return create_user(email=email, password=password, full_name=full_name)


def issue_access_token(user: User) -> str:
    roles, memberships = build_membership_claims(user)
    return issue_token(
        subject=str(user.id),
        token_type="access",
        expires_delta=settings.JWT_ACCESS_TOKEN_LIFETIME,
        claims={
            "email": user.email,
            "full_name": user.full_name,
            "roles": roles,
            "memberships": memberships,
            "tenant_access": build_tenant_access_claims(user),
        },
    )


def issue_refresh_token(user: User) -> str:
    return issue_token(
        subject=str(user.id),
        token_type="refresh",
        expires_delta=settings.JWT_REFRESH_TOKEN_LIFETIME,
        claims={
            "email": user.email,
        },
    )


def issue_token_pair(user: User) -> dict[str, object]:
    return {
        "access_token": issue_access_token(user),
        "refresh_token": issue_refresh_token(user),
        "token_type": "Bearer",
        "expires_in": settings.JWT_ACCESS_TTL_SECONDS,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "created_at": user.created_at.isoformat(),
        },
    }


def refresh_access_token(*, refresh_token: str) -> dict[str, object]:
    try:
        payload = verify_token(refresh_token, expected_token_type="refresh")
    except TokenError as exc:
        raise AuthenticationFailed(str(exc)) from exc

    user = get_user_by_id(payload.get("sub"))
    if not user or not user.is_active:
        raise AuthenticationFailed("User is inactive or missing")

    return {
        "access_token": issue_access_token(user),
        "token_type": "Bearer",
        "expires_in": settings.JWT_ACCESS_TTL_SECONDS,
    }
