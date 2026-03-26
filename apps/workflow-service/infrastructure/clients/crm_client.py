from __future__ import annotations

from django.conf import settings

from .base import BaseHTTPClient


class CRMClient(BaseHTTPClient):
    def __init__(self) -> None:
        super().__init__(
            service_name="crm-service",
            base_url=settings.CRM_SERVICE_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )

    def get_lead(self, token: str, lead_id: str):
        return self.get(f"/api/v1/internal/leads/{lead_id}/", token=token)

    def update_lead_workflow_state(self, token: str, lead_id: str, payload: dict[str, object]):
        return self.post(f"/api/v1/internal/leads/{lead_id}/workflow-update/", token=token, json_body=payload)
