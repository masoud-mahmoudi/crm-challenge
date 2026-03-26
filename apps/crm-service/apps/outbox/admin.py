from __future__ import annotations

from django.contrib import admin

from .models import OutboxEvent


@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "aggregate_type", "aggregate_id", "status", "retry_count", "published_at", "created_at")
    list_filter = ("event_type", "status")
    search_fields = ("event_type", "aggregate_id")
    readonly_fields = ("id", "created_at", "published_at")