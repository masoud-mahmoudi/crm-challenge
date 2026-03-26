from __future__ import annotations

import uuid
from typing import Any, Callable

from django.db import transaction
from django.utils import timezone

from .models import DeadLetterEvent, ProcessedMessage, WorkflowRun
from .selectors import get_dead_letter_by_event_id, get_workflow_run_by_event_id


EventHandler = Callable[[dict[str, Any]], dict[str, Any]]


def is_event_processed(event_id: str) -> bool:
    return ProcessedMessage.objects.filter(event_id=event_id).exists()


@transaction.atomic
def record_processed_message(event_id: str, topic: str, consumer_name: str) -> ProcessedMessage:
    processed_message, _ = ProcessedMessage.objects.get_or_create(
        event_id=uuid.UUID(str(event_id)),
        defaults={
            "topic": topic,
            "consumer_name": consumer_name,
        },
    )
    return processed_message


@transaction.atomic
def start_workflow_run(event: dict[str, Any]) -> WorkflowRun:
    payload = event.get("payload") or {}
    workflow_run, _ = WorkflowRun.objects.get_or_create(
        event_id=uuid.UUID(str(event["event_id"])),
        defaults={
            "event_type": str(event["event_type"]),
            "lead_id": payload.get("lead_id") or None,
            "company_id": payload.get("company_id") or None,
            "status": WorkflowRun.Status.RECEIVED,
        },
    )
    return workflow_run


@transaction.atomic
def mark_workflow_processing(workflow_run: WorkflowRun) -> WorkflowRun:
    workflow_run.status = WorkflowRun.Status.PROCESSING
    workflow_run.error_message = ""
    workflow_run.completed_at = None
    workflow_run.save(update_fields=["status", "error_message", "completed_at"])
    return workflow_run


@transaction.atomic
def mark_workflow_completed(workflow_run: WorkflowRun) -> WorkflowRun:
    workflow_run.status = WorkflowRun.Status.COMPLETED
    workflow_run.error_message = ""
    workflow_run.completed_at = timezone.now()
    workflow_run.save(update_fields=["status", "error_message", "completed_at"])
    return workflow_run


@transaction.atomic
def mark_workflow_failed(workflow_run: WorkflowRun, error_message: str) -> WorkflowRun:
    workflow_run.status = WorkflowRun.Status.FAILED
    workflow_run.retry_count += 1
    workflow_run.error_message = error_message[:2000]
    workflow_run.save(update_fields=["status", "retry_count", "error_message"])
    return workflow_run


@transaction.atomic
def mark_workflow_dead_lettered(workflow_run: WorkflowRun, error_message: str) -> WorkflowRun:
    workflow_run.status = WorkflowRun.Status.DEAD_LETTERED
    workflow_run.error_message = error_message[:2000]
    workflow_run.completed_at = timezone.now()
    workflow_run.save(update_fields=["status", "error_message", "completed_at"])
    return workflow_run


@transaction.atomic
def dead_letter_event(event: dict[str, Any], error_message: str) -> DeadLetterEvent:
    dead_letter, _ = DeadLetterEvent.objects.update_or_create(
        event_id=uuid.UUID(str(event["event_id"])),
        defaults={
            "topic": str(event.get("topic") or event.get("event_type") or "unknown"),
            "event_type": str(event["event_type"]),
            "payload": event,
            "error_message": error_message[:4000],
        },
    )
    return dead_letter


@transaction.atomic
def clear_dead_letter(event_id: str) -> None:
    DeadLetterEvent.objects.filter(event_id=event_id).delete()


@transaction.atomic
def replay_dead_letter(event_id: str, handler: EventHandler) -> dict[str, Any]:
    dead_letter = get_dead_letter_by_event_id(event_id)
    result = handler(dead_letter.payload)
    DeadLetterEvent.objects.filter(id=dead_letter.id).delete()
    return result


def get_or_create_workflow_run(event: dict[str, Any]) -> WorkflowRun:
    existing = get_workflow_run_by_event_id(str(event["event_id"]))
    return existing or start_workflow_run(event)
