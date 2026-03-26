from __future__ import annotations

from django.conf import settings

from .base import BaseHTTPClient


class WorkflowClient(BaseHTTPClient):
    def __init__(self) -> None:
        super().__init__(
            service_name="workflow-service",
            base_url=settings.WORKFLOW_SERVICE_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )

    def list_workflow_runs(self, token: str):
        return self.get("/api/v1/workflow-runs/", token=token)