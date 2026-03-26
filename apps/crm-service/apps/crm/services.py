from __future__ import annotations

from typing import Any

from auth_lib import AuthContext
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.outbox.publisher import publish_outbox_event_by_id
from apps.outbox.services import create_outbox_event
from infrastructure.kafka.topics import CRM_LEAD_CREATED_TOPIC

from .models import Lead
from .permissions import can_assign_lead, require_company_access, require_lead_access


def create_lead(auth_context: AuthContext, validated_data: dict[str, Any]) -> Lead:
    company_id = require_company_access(auth_context, str(validated_data["company_id"]))

    with transaction.atomic():
        lead = Lead.objects.create(
            company_id=company_id,
            owner_user_id=validated_data.get("owner_user_id"),
            created_by_user_id=auth_context.user_id,
            name=validated_data["name"],
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            source=validated_data.get("source"),
            status=Lead.Status.NEW,
            enrichment_status=Lead.EnrichmentStatus.PENDING,
            score=None,
        )
        outbox_event = create_outbox_event(
            event_type=CRM_LEAD_CREATED_TOPIC,
            aggregate_type="lead",
            aggregate_id=lead.id,
            payload={
                "lead_id": str(lead.id),
                "company_id": str(lead.company_id),
                "created_by_user_id": str(lead.created_by_user_id),
            },
            headers={
                "producer": "crm-service",
                "schema_version": "1.0.0",
                "trace_id": auth_context.claims.get("jti"),
            },
        )
        transaction.on_commit(lambda: publish_outbox_event_by_id(str(outbox_event.id)))
    return lead


def update_lead(auth_context: AuthContext, lead: Lead, validated_data: dict[str, Any]) -> Lead:
    lead = require_lead_access(auth_context, lead)
    for field in ("name", "email", "phone", "source", "status"):
        if field in validated_data:
            setattr(lead, field, validated_data[field])
    lead.save(update_fields=[field for field in ("name", "email", "phone", "source", "status", "updated_at") if field in validated_data or field == "updated_at"])
    return lead


def assign_lead(auth_context: AuthContext, lead: Lead, owner_user_id: str) -> Lead:
    if not can_assign_lead(auth_context, lead):
        raise PermissionDenied("You are not allowed to assign this lead")
    lead.owner_user_id = owner_user_id
    lead.save(update_fields=["owner_user_id", "updated_at"])
    return lead


def update_lead_workflow_state(lead: Lead, validated_data: dict[str, Any]) -> Lead:
    for field in ("enrichment_status", "score", "status"):
        if field in validated_data:
            setattr(lead, field, validated_data[field])
    lead.save(
        update_fields=[
            field
            for field in ("enrichment_status", "score", "status", "updated_at")
            if field in validated_data or field == "updated_at"
        ]
    )
    return lead