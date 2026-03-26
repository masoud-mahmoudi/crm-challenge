from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.workflows.consumers import consume_forever


class Command(BaseCommand):
    help = "Consume workflow events from Kafka"

    def handle(self, *args, **options):
        consume_forever()
