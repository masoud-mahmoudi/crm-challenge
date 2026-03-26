from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructure.auth.service_tokens import get_internal_service_token
from infrastructure.clients.crm_client import CRMClient

from .consumers import dispatch_event
from .permissions import IsAuthenticatedWorkflowUser, IsWorkflowAdmin
from .selectors import get_workflow_run_by_id, list_dead_letters, list_workflow_runs
from .serializers import DeadLetterEventSerializer, WorkflowRunSerializer
from .services import replay_dead_letter


class WorkflowRunListView(APIView):
    permission_classes = [IsAuthenticatedWorkflowUser]

    def get(self, request, *args, **kwargs):
        queryset = list_workflow_runs(
            {
                "status": request.query_params.get("status"),
                "event_type": request.query_params.get("event_type"),
                "lead_id": request.query_params.get("lead_id"),
            }
        )
        return Response(WorkflowRunSerializer(queryset, many=True).data, status=status.HTTP_200_OK)


class WorkflowRunDetailView(APIView):
    permission_classes = [IsAuthenticatedWorkflowUser]

    def get(self, request, run_id: str, *args, **kwargs):
        workflow_run = get_workflow_run_by_id(run_id)
        return Response(WorkflowRunSerializer(workflow_run).data, status=status.HTTP_200_OK)


class DeadLetterListView(APIView):
    permission_classes = [IsWorkflowAdmin]

    def get(self, request, *args, **kwargs):
        return Response(DeadLetterEventSerializer(list_dead_letters(), many=True).data, status=status.HTTP_200_OK)


class ReplayWorkflowEventView(APIView):
    permission_classes = [IsWorkflowAdmin]

    def post(self, request, event_id: str, *args, **kwargs):
        crm_client = CRMClient()
        result = replay_dead_letter(
            event_id,
            handler=lambda event: dispatch_event(
                event,
                crm_client=crm_client,
                service_token=get_internal_service_token(),
            ),
        )
        return Response(result, status=status.HTTP_200_OK)
