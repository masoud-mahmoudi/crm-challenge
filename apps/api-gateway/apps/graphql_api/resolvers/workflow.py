from __future__ import annotations

from strawberry import Info

from apps.graphql_api.types import WorkflowRun
from infrastructure.auth.decorators import require_graphql_auth


def resolve_workflow_runs(info: Info) -> list[WorkflowRun]:
    auth_context = require_graphql_auth(info)
    workflow_runs = info.context.services.workflow_service.list_workflow_runs(token=auth_context.token)
    return [WorkflowRun.from_dict(item) for item in workflow_runs]