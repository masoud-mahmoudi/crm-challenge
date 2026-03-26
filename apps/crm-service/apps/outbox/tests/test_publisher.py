from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from apps.outbox.models import OutboxEvent
from apps.outbox.publisher import publish_outbox_event, publish_outbox_event_by_id, publish_pending_events


class OutboxPublisherTests(TestCase):
    @patch("apps.outbox.publisher.publish_event")
    def test_publish_outbox_event_marks_single_event_published(self, mock_publish_event):
        event = OutboxEvent.objects.create(
            event_type="crm.lead.created",
            aggregate_type="lead",
            aggregate_id="11111111-1111-1111-1111-111111111111",
            payload={"lead_id": "11111111-1111-1111-1111-111111111111"},
        )

        result = publish_outbox_event(event)

        self.assertTrue(result)
        event.refresh_from_db()
        self.assertEqual(event.status, OutboxEvent.Status.PUBLISHED)

    @patch("apps.outbox.publisher.publish_event")
    def test_publish_outbox_event_by_id_retries_failed_event(self, mock_publish_event):
        event = OutboxEvent.objects.create(
            event_type="crm.lead.created",
            aggregate_type="lead",
            aggregate_id="11111111-1111-1111-1111-111111111111",
            payload={"lead_id": "11111111-1111-1111-1111-111111111111"},
            status=OutboxEvent.Status.FAILED,
            retry_count=1,
        )

        result = publish_outbox_event_by_id(str(event.id))

        self.assertTrue(result)
        event.refresh_from_db()
        self.assertEqual(event.status, OutboxEvent.Status.PUBLISHED)

    @patch("apps.outbox.publisher.publish_event")
    def test_publish_pending_events_marks_event_published(self, mock_publish_event):
        OutboxEvent.objects.create(
            event_type="crm.lead.created",
            aggregate_type="lead",
            aggregate_id="11111111-1111-1111-1111-111111111111",
            payload={"lead_id": "11111111-1111-1111-1111-111111111111"},
        )

        result = publish_pending_events()

        self.assertEqual(result["published"], 1)
        self.assertEqual(OutboxEvent.objects.first().status, OutboxEvent.Status.PUBLISHED)

    @patch("apps.outbox.publisher.publish_event")
    def test_publish_pending_events_includes_failed_events(self, mock_publish_event):
        OutboxEvent.objects.create(
            event_type="crm.lead.created",
            aggregate_type="lead",
            aggregate_id="11111111-1111-1111-1111-111111111111",
            payload={"lead_id": "11111111-1111-1111-1111-111111111111"},
            status=OutboxEvent.Status.FAILED,
            retry_count=1,
        )

        result = publish_pending_events()

        self.assertEqual(result["published"], 1)
        self.assertEqual(OutboxEvent.objects.first().status, OutboxEvent.Status.PUBLISHED)