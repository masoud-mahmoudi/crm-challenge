from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from kafka import KafkaProducer


_producer: KafkaProducer | None = None


def get_kafka_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8"),
        )
    return _producer


def publish_event(topic: str, key: str, payload: dict[str, Any], headers: dict[str, Any] | None = None) -> None:
    producer = get_kafka_producer()
    kafka_headers = []
    for header_key, header_value in (headers or {}).items():
        if header_value is None:
            continue
        kafka_headers.append((str(header_key), str(header_value).encode("utf-8")))
    future = producer.send(topic, key=key, value=payload, headers=kafka_headers)
    future.get(timeout=10)