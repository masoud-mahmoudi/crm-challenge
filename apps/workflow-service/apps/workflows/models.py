from __future__ import annotations

import uuid

from django.db import models


class ProcessedMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(unique=True, db_index=True)
    topic = models.CharField(max_length=128)
    consumer_name = models.CharField(max_length=128)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-processed_at",)
        indexes = [
            models.Index(fields=("topic", "consumer_name"), name="wf_msg_topic_consumer_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.event_id} ({self.consumer_name})"


class WorkflowRun(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        DEAD_LETTERED = "DEAD_LETTERED", "Dead lettered"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=128, db_index=True)
    lead_id = models.UUIDField(null=True, blank=True, db_index=True)
    company_id = models.UUIDField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.RECEIVED)
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)
        indexes = [
            models.Index(fields=("status", "event_type"), name="workflow_run_status_event_idx"),
            models.Index(fields=("lead_id",), name="workflow_run_lead_idx"),
            models.Index(fields=("company_id",), name="workflow_run_company_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.status})"


class DeadLetterEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(db_index=True)
    topic = models.CharField(max_length=128)
    event_type = models.CharField(max_length=128)
    payload = models.JSONField()
    error_message = models.TextField()
    failed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-failed_at",)
        indexes = [
            models.Index(fields=("event_type",), name="workflow_dlq_event_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.event_id})"
