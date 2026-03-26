from __future__ import annotations

import json

from django.conf import settings
from kafka import KafkaProducer


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def publish_event(topic: str, payload: dict[str, object]) -> None:
    producer = build_producer()
    try:
        producer.send(topic, payload).get(timeout=10)
        producer.flush()
    finally:
        producer.close()
