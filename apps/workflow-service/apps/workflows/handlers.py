from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

from infrastructure.clients.crm_client import CRMClient

from .dlq import move_to_dead_letter
from .retries import should_retry
from .services import (
    clear_dead_letter,
    get_or_create_workflow_run,
    is_event_processed,
    mark_workflow_completed,
    mark_workflow_dead_lettered,
    mark_workflow_failed,
    mark_workflow_processing,
    record_processed_message,
)


logger = logging.getLogger(__name__)


def build_enrichment_payload(lead: dict[str, Any]) -> dict[str, Any]:
    email_present = bool(lead.get("email"))
    phone_present = bool(lead.get("phone"))

    if email_present and phone_present:
        score = 85
        status = "QUALIFIED"
    elif email_present or phone_present:
        score = 60
        status = "REVIEW_REQUIRED"
    else:
        score = 30
        status = "UNQUALIFIED"

    return {
        "enrichment_status": "COMPLETED",
        "score": score,
        "status": status,
    }


def handle_lead_created(
    event: dict[str, Any],
    *,
    crm_client: CRMClient,
    service_token: str,
    consumer_name: str = "workflow-service",
    max_retries: int | None = None,
) -> dict[str, Any]:
    event_id = str(event["event_id"])
    topic = str(event.get("topic") or event.get("event_type") or "crm.lead.created")
    payload = event.get("payload") or {}
    lead_id = str(payload["lead_id"])
    max_retry_count = max_retries or settings.WORKFLOW_MAX_RETRIES

    if is_event_processed(event_id):
        logger.info("Skipping duplicate workflow event %s", event_id)
        return {"status": "duplicate", "event_id": event_id}

    workflow_run = get_or_create_workflow_run(event)

    while True:
        mark_workflow_processing(workflow_run)
        try:
            lead = crm_client.get_lead(service_token, lead_id)
            update_payload = build_enrichment_payload(lead)
            crm_client.update_lead_workflow_state(service_token, lead_id, update_payload)
            mark_workflow_completed(workflow_run)
            record_processed_message(event_id, topic, consumer_name)
            clear_dead_letter(event_id)
            return {
                "status": "completed",
                "event_id": event_id,
                "workflow_run_id": str(workflow_run.id),
                "lead_id": lead_id,
                "update": update_payload,
            }
        except Exception as exc:
            logger.warning("Workflow processing failed for event %s: %s", event_id, exc)
            workflow_run = mark_workflow_failed(workflow_run, str(exc))
            if should_retry(workflow_run.retry_count, max_retry_count):
                continue
            move_to_dead_letter(event, str(exc))
            mark_workflow_dead_lettered(workflow_run, str(exc))
            raise
