from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrastructure.clients.crm_client import CRMClient


@dataclass
class ActivityService:
    crm_client: CRMClient

    def list_activities(self, *, token: str, lead_id: str | None = None) -> list[dict[str, Any]]:
        return []

    def create_activity(self, *, token: str, payload: dict[str, object]) -> dict[str, Any]:
        return {}