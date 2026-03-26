from __future__ import annotations

import logging
from typing import Any

from infrastructure.auth.service_tokens import get_internal_service_token
from infrastructure.clients.crm_client import CRMClient
from infrastructure.kafka.consumer import build_consumer
from infrastructure.kafka.topics import CRM_LEAD_CREATED_TOPIC

from .handlers import handle_lead_created


logger = logging.getLogger(__name__)


def parse_event(topic: str, raw_value: Any) -> dict[str, Any]:
    if not isinstance(raw_value, dict):
        raise ValueError("Kafka event payload must deserialize to a dictionary")

    event = dict(raw_value)
    event.setdefault("topic", topic)
    for required_field in ("event_id", "event_type", "payload"):
        if required_field not in event:
            raise ValueError(f"Kafka event missing required field '{required_field}'")
    return event


def dispatch_event(event: dict[str, Any], *, crm_client: CRMClient, service_token: str) -> dict[str, Any]:
    event_type = str(event.get("event_type") or "")
    if event_type == CRM_LEAD_CREATED_TOPIC:
        return handle_lead_created(event, crm_client=crm_client, service_token=service_token, consumer_name="workflow-consumer")

    logger.info("Ignoring unsupported workflow event type %s", event_type)
    return {"status": "ignored", "event_type": event_type}


def consume_forever() -> None:
    consumer = build_consumer([CRM_LEAD_CREATED_TOPIC])
    crm_client = CRMClient()
    service_token = get_internal_service_token()

    logger.info("Workflow consumer started for topic %s", CRM_LEAD_CREATED_TOPIC)
    try:
        for message in consumer:
            try:
                event = parse_event(message.topic, message.value)
                dispatch_event(event, crm_client=crm_client, service_token=service_token)
            except Exception as exc:  # pragma: no cover - infinite loop path
                logger.exception("Workflow consumer failed to process Kafka message: %s", exc)
    finally:  # pragma: no cover - cleanup path
        consumer.close()
