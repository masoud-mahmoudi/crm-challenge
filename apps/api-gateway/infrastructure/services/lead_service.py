from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrastructure.clients.crm_client import CRMClient


@dataclass
class LeadService:
    crm_client: CRMClient

    def list_leads(
        self,
        *,
        token: str,
        status: str | None = None,
        company_id: str | None = None,
    ) -> list[dict[str, Any]]:
        response = self.crm_client.list_leads(token, status=status, company_id=company_id)
        return response if isinstance(response, list) else []

    def get_lead(self, *, token: str, lead_id: str) -> dict[str, Any]:
        response = self.crm_client.get_lead(token, lead_id)
        return response if isinstance(response, dict) else {}

    def create_lead(self, *, token: str, payload: dict[str, object]) -> dict[str, Any]:
        response = self.crm_client.create_lead(token, payload)
        return response if isinstance(response, dict) else {}

    def update_lead(self, *, token: str, lead_id: str, payload: dict[str, object]) -> dict[str, Any]:
        response = self.crm_client.update_lead(token, lead_id, payload)
        return response if isinstance(response, dict) else {}

    def assign_lead(self, *, token: str, lead_id: str, owner_user_id: str) -> dict[str, Any]:
        response = self.crm_client.assign_lead(token, lead_id, owner_user_id)
        return response if isinstance(response, dict) else {}