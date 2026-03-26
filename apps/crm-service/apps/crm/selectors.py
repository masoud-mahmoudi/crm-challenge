from __future__ import annotations

from typing import Any

from auth_lib import AuthContext
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Lead
from .permissions import get_accessible_company_ids, require_company_access, require_lead_access


def list_leads_for_user(auth_context: AuthContext, filters: dict[str, Any] | None = None) -> QuerySet[Lead]:
    queryset = Lead.objects.filter(company_id__in=get_accessible_company_ids(auth_context)).order_by("-created_at")
    applied_filters = filters or {}

    status_value = applied_filters.get("status")
    if status_value:
        queryset = queryset.filter(status=status_value)

    company_id = applied_filters.get("company_id")
    if company_id:
        require_company_access(auth_context, str(company_id))
        queryset = queryset.filter(company_id=company_id)

    return queryset


def get_lead_for_user(auth_context: AuthContext, lead_id: str) -> Lead:
    lead = Lead.objects.filter(id=lead_id).first()
    if not lead:
        raise NotFound("Lead not found")
    return require_lead_access(auth_context, lead)


def get_lead_by_id(lead_id: str) -> Lead:
    lead = Lead.objects.filter(id=lead_id).first()
    if not lead:
        raise NotFound("Lead not found")
    return lead