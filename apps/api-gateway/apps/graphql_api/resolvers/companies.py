from __future__ import annotations

from strawberry import Info

from apps.graphql_api.types import Company, MePayload
from infrastructure.auth.decorators import require_graphql_auth


def resolve_me(info: Info) -> MePayload:
    auth_context = require_graphql_auth(info)
    payload = info.context.services.auth_service.me(auth_context=auth_context)
    return MePayload.from_dict(payload)


def resolve_companies(info: Info) -> list[Company]:
    auth_context = require_graphql_auth(info)
    companies = info.context.services.company_service.list_companies(token=auth_context.token)
    return [Company.from_dict(item) for item in companies]