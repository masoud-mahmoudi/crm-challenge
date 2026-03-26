from __future__ import annotations

from django.test import TestCase

from apps.workflows.models import ProcessedMessage, WorkflowRun
from apps.workflows.services import record_processed_message, start_workflow_run


def build_event() -> dict[str, object]:
    return {
        "event_id": "11111111-1111-1111-1111-111111111111",
        "event_type": "crm.lead.created",
        "topic": "crm.lead.created",
        "payload": {
            "lead_id": "22222222-2222-2222-2222-222222222222",
            "company_id": "33333333-3333-3333-3333-333333333333",
            "created_by_user_id": "44444444-4444-4444-4444-444444444444",
        },
    }


class WorkflowServiceTests(TestCase):
    def test_processed_message_idempotency(self):
        event = build_event()
        first = record_processed_message(str(event["event_id"]), str(event["topic"]), "workflow-consumer")
        second = record_processed_message(str(event["event_id"]), str(event["topic"]), "workflow-consumer")

        self.assertEqual(first.id, second.id)
        self.assertEqual(ProcessedMessage.objects.count(), 1)

    def test_start_workflow_run_creates_record(self):
        workflow_run = start_workflow_run(build_event())

        self.assertEqual(workflow_run.status, WorkflowRun.Status.RECEIVED)
        self.assertEqual(str(workflow_run.lead_id), "22222222-2222-2222-2222-222222222222")
        self.assertEqual(WorkflowRun.objects.count(), 1)
