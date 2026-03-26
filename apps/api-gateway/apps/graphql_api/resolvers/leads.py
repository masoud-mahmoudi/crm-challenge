from __future__ import annotations

from strawberry import Info

from apps.graphql_api.types import CreateLeadInput, Lead, UpdateLeadInput
from infrastructure.auth.decorators import require_graphql_auth


def resolve_leads(info: Info, status: str | None = None, company_id: str | None = None) -> list[Lead]:
    auth_context = require_graphql_auth(info)
    leads = info.context.services.lead_service.list_leads(
        token=auth_context.token,
        status=status,
        company_id=company_id,
    )
    return [Lead.from_dict(item) for item in leads]


def resolve_lead(info: Info, lead_id: str) -> Lead:
    auth_context = require_graphql_auth(info)
    lead = info.context.services.lead_service.get_lead(token=auth_context.token, lead_id=lead_id)
    return Lead.from_dict(lead)


def mutate_create_lead(info: Info, input: CreateLeadInput) -> Lead:
    auth_context = require_graphql_auth(info)
    lead = info.context.services.lead_service.create_lead(
        token=auth_context.token,
        payload={
            "name": input.name or input.title,
            "company_id": input.company_id,
            "owner_user_id": input.owner_user_id,
            "source": input.source,
            "email": input.email,
            "phone": input.phone,
        },
    )
    return Lead.from_dict(lead)


def mutate_update_lead(info: Info, lead_id: str, input: UpdateLeadInput) -> Lead:
    auth_context = require_graphql_auth(info)
    payload = {
        "name": input.name or input.title,
        "email": input.email,
        "phone": input.phone,
        "source": input.source,
        "status": input.status,
    }
    lead = info.context.services.lead_service.update_lead(
        token=auth_context.token,
        lead_id=lead_id,
        payload={key: value for key, value in payload.items() if value is not None},
    )
    return Lead.from_dict(lead)


def mutate_assign_lead(info: Info, lead_id: str, owner_user_id: str) -> Lead:
    auth_context = require_graphql_auth(info)
    lead = info.context.services.lead_service.assign_lead(
        token=auth_context.token,
        lead_id=lead_id,
        owner_user_id=owner_user_id,
    )
    return Lead.from_dict(lead)