from __future__ import annotations

import logging
from uuid import UUID

from apps.outbox.selectors import get_publishable_event, list_publishable_events
from apps.outbox.services import mark_failed, mark_published
from infrastructure.kafka.producer import publish_event


logger = logging.getLogger(__name__)


def publish_outbox_event(event) -> bool:
    envelope = {
        "event_id": str(event.id),
        "event_type": event.event_type,
        "occurred_at": event.created_at.isoformat(),
        "producer": event.headers.get("producer", "crm-service"),
        "schema_version": event.headers.get("schema_version", "1.0.0"),
        "trace_id": event.headers.get("trace_id"),
        "payload": event.payload,
    }
    try:
        publish_event(topic=event.event_type, key=str(event.aggregate_id), payload=envelope, headers=event.headers)
        mark_published(event)
        return True
    except Exception as exc:
        logger.warning("Failed to publish outbox event %s: %s", event.id, exc)
        mark_failed(event)
        return False


def publish_outbox_event_by_id(event_id: str) -> bool:
    event = get_publishable_event(str(UUID(str(event_id))))
    if event is None:
        return False
    return publish_outbox_event(event)


def publish_pending_events(limit: int = 100) -> dict[str, int]:
    published = 0
    failed = 0
    for event in list_publishable_events(limit=limit):
        if publish_outbox_event(event):
            published += 1
        else:
            failed += 1
    return {"published": published, "failed": failed}