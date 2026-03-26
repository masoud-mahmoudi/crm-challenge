from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404

from .models import DeadLetterEvent, WorkflowRun


def get_workflow_run_by_id(run_id: str) -> WorkflowRun:
    return get_object_or_404(WorkflowRun, id=run_id)


def get_workflow_run_by_event_id(event_id: str) -> WorkflowRun | None:
    return WorkflowRun.objects.filter(event_id=event_id).first()


def list_workflow_runs(filters: dict[str, Any] | None = None):
    queryset = WorkflowRun.objects.all()
    filters = filters or {}
    if filters.get("status"):
        queryset = queryset.filter(status=filters["status"])
    if filters.get("event_type"):
        queryset = queryset.filter(event_type=filters["event_type"])
    if filters.get("lead_id"):
        queryset = queryset.filter(lead_id=filters["lead_id"])
    return queryset


def get_dead_letter_by_event_id(event_id: str) -> DeadLetterEvent:
    return get_object_or_404(DeadLetterEvent, event_id=event_id)


def list_dead_letters():
    return DeadLetterEvent.objects.all()
