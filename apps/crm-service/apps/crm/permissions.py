from __future__ import annotations

from auth_lib import AuthContext, AuthError
from rest_framework.exceptions import PermissionDenied

from .models import Lead


def get_accessible_company_ids(auth_context: AuthContext) -> set[str]:
    return {str(company_id) for company_id in auth_context.tenant_access.data_company_ids}


def can_access_company(auth_context: AuthContext, company_id: str) -> bool:
    return auth_context.can_access_company(str(company_id), data_scope=True)


def require_company_access(auth_context: AuthContext, company_id: str) -> str:
    try:
        return auth_context.require_company_access(str(company_id), data_scope=True)
    except AuthError as exc:
        raise PermissionDenied(str(exc)) from exc


def can_access_lead(auth_context: AuthContext, lead: Lead) -> bool:
    return can_access_company(auth_context, str(lead.company_id))


def require_lead_access(auth_context: AuthContext, lead: Lead) -> Lead:
    if not can_access_lead(auth_context, lead):
        raise PermissionDenied("You are not allowed to access this lead")
    return lead


def can_assign_lead(auth_context: AuthContext, lead: Lead) -> bool:
    return can_access_lead(auth_context, lead)