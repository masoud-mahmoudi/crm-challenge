from __future__ import annotations

import logging
from typing import Any

from infrastructure.kafka.producer import publish_event
from infrastructure.kafka.topics import WORKFLOW_DEAD_LETTER_TOPIC

from .services import dead_letter_event


logger = logging.getLogger(__name__)


def move_to_dead_letter(event: dict[str, Any], error_message: str) -> None:
    dead_letter = dead_letter_event(event, error_message)
    try:
        publish_event(
            WORKFLOW_DEAD_LETTER_TOPIC,
            {
                "event_id": str(dead_letter.event_id),
                "event_type": dead_letter.event_type,
                "topic": dead_letter.topic,
                "payload": dead_letter.payload,
                "error_message": dead_letter.error_message,
            },
        )
    except Exception as exc:  # pragma: no cover - best effort logging path
        logger.warning("Failed to publish dead-letter event %s: %s", dead_letter.event_id, exc)
