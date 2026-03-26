from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.outbox.publisher import publish_pending_events


class Command(BaseCommand):
    help = "Publish pending outbox events to Kafka"

    def handle(self, *args, **options):
        result = publish_pending_events()
        self.stdout.write(self.style.SUCCESS(f"Published {result['published']} events; {result['failed']} failed."))