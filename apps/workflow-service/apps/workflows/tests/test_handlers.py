from __future__ import annotations

from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from apps.workflows.handlers import build_enrichment_payload, handle_lead_created
from apps.workflows.models import DeadLetterEvent, ProcessedMessage, WorkflowRun


def build_event(event_id: str = "11111111-1111-1111-1111-111111111111") -> dict[str, object]:
    return {
        "event_id": event_id,
        "event_type": "crm.lead.created",
        "topic": "crm.lead.created",
        "payload": {
            "lead_id": "22222222-2222-2222-2222-222222222222",
            "company_id": "33333333-3333-3333-3333-333333333333",
            "created_by_user_id": "44444444-4444-4444-4444-444444444444",
        },
    }


class LeadCreatedHandlerTests(TestCase):
    def test_enrichment_payload_scores_complete_contact_details(self):
        payload = build_enrichment_payload({"email": "lead@example.com", "phone": "123"})

        self.assertEqual(payload["score"], 85)
        self.assertEqual(payload["status"], "QUALIFIED")

    def test_handle_lead_created_success(self):
        crm_client = Mock()
        crm_client.get_lead.return_value = {"id": "222", "email": "lead@example.com", "phone": "123"}
        crm_client.update_lead_workflow_state.return_value = {"status": "updated"}

        result = handle_lead_created(build_event(), crm_client=crm_client, service_token="internal-token")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(ProcessedMessage.objects.count(), 1)
        self.assertEqual(WorkflowRun.objects.get().status, WorkflowRun.Status.COMPLETED)
        crm_client.update_lead_workflow_state.assert_called_once()

    def test_duplicate_event_is_skipped(self):
        crm_client = Mock()
        crm_client.get_lead.return_value = {"id": "222", "email": "lead@example.com", "phone": "123"}
        crm_client.update_lead_workflow_state.return_value = {"status": "updated"}
        event = build_event()
        handle_lead_created(event, crm_client=crm_client, service_token="internal-token")

        result = handle_lead_created(event, crm_client=crm_client, service_token="internal-token")

        self.assertEqual(result["status"], "duplicate")
        self.assertEqual(crm_client.update_lead_workflow_state.call_count, 1)

    @override_settings(WORKFLOW_MAX_RETRIES=2)
    @patch("apps.workflows.dlq.publish_event")
    def test_dead_letter_created_on_repeated_failure(self, mock_publish_event):
        crm_client = Mock()
        crm_client.get_lead.side_effect = RuntimeError("crm unavailable")

        with self.assertRaises(RuntimeError):
            handle_lead_created(build_event("55555555-5555-5555-5555-555555555555"), crm_client=crm_client, service_token="internal-token")

        workflow_run = WorkflowRun.objects.get(event_id="55555555-5555-5555-5555-555555555555")
        self.assertEqual(workflow_run.status, WorkflowRun.Status.DEAD_LETTERED)
        self.assertEqual(workflow_run.retry_count, 2)
        self.assertEqual(DeadLetterEvent.objects.count(), 1)
        mock_publish_event.assert_called_once()

    def test_crm_client_update_call_payload(self):
        crm_client = Mock()
        crm_client.get_lead.return_value = {"id": "222", "email": "lead@example.com", "phone": None}
        crm_client.update_lead_workflow_state.return_value = {"status": "updated"}

        handle_lead_created(build_event("66666666-6666-6666-6666-666666666666"), crm_client=crm_client, service_token="internal-token")

        args, _ = crm_client.update_lead_workflow_state.call_args
        self.assertEqual(args[2]["score"], 60)
        self.assertEqual(args[2]["status"], "REVIEW_REQUIRED")
