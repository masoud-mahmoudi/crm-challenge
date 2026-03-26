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

    def list_leads(
        self,
        token: str,
        *,
        status: str | None = None,
        company_id: str | None = None,
    ):
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if company_id:
            params["company_id"] = company_id
        return self.get("/api/v1/leads/", token=token, params=params or None)

    def get_lead(self, token: str, lead_id: str):
        return self.get(f"/api/v1/leads/{lead_id}/", token=token)

    def create_lead(self, token: str, payload: dict[str, object]):
        return self.post("/api/v1/leads/", token=token, json_body=payload)

    def update_lead(self, token: str, lead_id: str, payload: dict[str, object]):
        return self.request("PATCH", f"/api/v1/leads/{lead_id}/", token=token, json_body=payload)

    def assign_lead(self, token: str, lead_id: str, owner_user_id: str):
        return self.post(
            f"/api/v1/leads/{lead_id}/assign/",
            token=token,
            json_body={"owner_user_id": owner_user_id},
        )

    def list_activities(self, token: str, lead_id: str | None = None):
        params = {"lead_id": lead_id} if lead_id else None
        return self.get("/api/v1/activities/", token=token, params=params)

    def create_activity(self, token: str, payload: dict[str, object]):
        return self.post("/api/v1/activities/", token=token, json_body=payload)