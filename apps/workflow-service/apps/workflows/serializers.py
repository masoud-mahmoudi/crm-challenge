from __future__ import annotations

from rest_framework import serializers

from .models import DeadLetterEvent, WorkflowRun


class WorkflowRunSerializer(serializers.ModelSerializer):
    workflow_name = serializers.SerializerMethodField()
    finished_at = serializers.DateTimeField(source="completed_at", read_only=True)

    class Meta:
        model = WorkflowRun
        fields = (
            "id",
            "workflow_name",
            "event_id",
            "event_type",
            "lead_id",
            "company_id",
            "status",
            "retry_count",
            "error_message",
            "started_at",
            "completed_at",
            "finished_at",
        )

    def get_workflow_name(self, obj: WorkflowRun) -> str:
        if obj.event_type == "crm.lead.created":
            return "lead_enrichment"
        return obj.event_type


class DeadLetterEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadLetterEvent
        fields = (
            "id",
            "event_id",
            "topic",
            "event_type",
            "payload",
            "error_message",
            "failed_at",
        )
