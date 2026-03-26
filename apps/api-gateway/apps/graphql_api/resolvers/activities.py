from __future__ import annotations

from strawberry import Info

from apps.graphql_api.types import Activity, CreateActivityInput
from infrastructure.auth.decorators import require_graphql_auth


def resolve_activities(info: Info, lead_id: str | None = None) -> list[Activity]:
    auth_context = require_graphql_auth(info)
    activities = info.context.services.activity_service.list_activities(
        token=auth_context.token,
        lead_id=lead_id,
    )
    return [Activity.from_dict(item) for item in activities]


def mutate_create_activity(info: Info, input: CreateActivityInput) -> Activity:
    auth_context = require_graphql_auth(info)
    activity = info.context.services.activity_service.create_activity(
        token=auth_context.token,
        payload={
            "lead_id": input.lead_id,
            "type": input.type,
            "summary": input.summary,
        },
    )
    return Activity.from_dict(activity)