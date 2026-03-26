from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrastructure.clients.workflow_client import WorkflowClient


@dataclass
class WorkflowService:
    workflow_client: WorkflowClient

    def list_workflow_runs(self, *, token: str) -> list[dict[str, Any]]:
        response = self.workflow_client.list_workflow_runs(token)
        return response if isinstance(response, list) else []