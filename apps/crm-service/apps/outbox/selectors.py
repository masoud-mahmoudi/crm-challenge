from __future__ import annotations

from django.db.models import QuerySet

from .models import OutboxEvent


def list_publishable_events(limit: int = 100) -> QuerySet[OutboxEvent]:
    return OutboxEvent.objects.filter(
        status__in=(OutboxEvent.Status.PENDING, OutboxEvent.Status.FAILED)
    ).order_by("created_at")[:limit]


def get_publishable_event(event_id: str) -> OutboxEvent | None:
    return OutboxEvent.objects.filter(
        id=event_id,
        status__in=(OutboxEvent.Status.PENDING, OutboxEvent.Status.FAILED),
    ).first()