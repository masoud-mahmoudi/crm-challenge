from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.outbox.models import OutboxEvent


def create_outbox_event(
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id,
    payload: dict[str, Any],
    headers: dict[str, Any] | None = None,
) -> OutboxEvent:
    return OutboxEvent.objects.create(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        headers=headers or {},
        status=OutboxEvent.Status.PENDING,
    )


def mark_published(event: OutboxEvent) -> OutboxEvent:
    event.status = OutboxEvent.Status.PUBLISHED
    event.published_at = datetime.now(tz=timezone.utc)
    event.save(update_fields=["status", "published_at"])
    return event


def mark_failed(event: OutboxEvent) -> OutboxEvent:
    event.status = OutboxEvent.Status.FAILED
    event.retry_count += 1
    event.save(update_fields=["status", "retry_count"])
    return event