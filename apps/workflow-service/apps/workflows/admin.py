from __future__ import annotations

from django.contrib import admin

from .models import DeadLetterEvent, ProcessedMessage, WorkflowRun


@admin.register(ProcessedMessage)
class ProcessedMessageAdmin(admin.ModelAdmin):
    list_display = ("event_id", "topic", "consumer_name", "processed_at")
    search_fields = ("event_id", "topic", "consumer_name")
    list_filter = ("topic", "consumer_name")


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "lead_id", "status", "retry_count", "started_at", "completed_at")
    search_fields = ("event_id", "lead_id", "company_id")
    list_filter = ("status", "event_type")


@admin.register(DeadLetterEvent)
class DeadLetterEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "topic", "event_type", "failed_at")
    search_fields = ("event_id", "topic", "event_type")
    list_filter = ("topic", "event_type")
