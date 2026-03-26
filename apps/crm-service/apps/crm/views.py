from __future__ import annotations

from auth_lib import AuthContext
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import cast

from infrastructure.auth.decorators import require_request_auth
from infrastructure.auth.service_tokens import require_internal_service_token

from .selectors import get_lead_by_id, get_lead_for_user, list_leads_for_user
from .serializers import AssignLeadSerializer, CreateLeadSerializer, InternalLeadWorkflowUpdateSerializer, LeadDetailSerializer, LeadListSerializer, UpdateLeadSerializer
from .services import assign_lead, create_lead, update_lead, update_lead_workflow_state


class LeadListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_auth_context(self, request) -> AuthContext:
        return require_request_auth(request)

    def get(self, request, *args, **kwargs):
        auth_context = self.get_auth_context(request)
        queryset = list_leads_for_user(
            auth_context,
            filters={
                "status": request.query_params.get("status"),
                "company_id": request.query_params.get("company_id"),
            },
        )
        serializer = LeadListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        auth_context = self.get_auth_context(request)
        serializer = CreateLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, object], serializer.validated_data)
        lead = create_lead(auth_context, payload)
        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_201_CREATED)


class LeadDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_auth_context(self, request) -> AuthContext:
        return require_request_auth(request)

    def get(self, request, lead_id: str, *args, **kwargs):
        auth_context = self.get_auth_context(request)
        lead = get_lead_for_user(auth_context, lead_id)
        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_200_OK)

    def patch(self, request, lead_id: str, *args, **kwargs):
        auth_context = self.get_auth_context(request)
        serializer = UpdateLeadSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        lead = get_lead_for_user(auth_context, lead_id)
        updated_lead = update_lead(auth_context, lead, cast(dict[str, object], serializer.validated_data))
        return Response(LeadDetailSerializer(updated_lead).data, status=status.HTTP_200_OK)


class LeadAssignView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, lead_id: str, *args, **kwargs):
        auth_context = require_request_auth(request)
        serializer = AssignLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, object], serializer.validated_data)
        lead = get_lead_for_user(auth_context, lead_id)
        updated_lead = assign_lead(
            auth_context,
            lead,
            str(payload["owner_user_id"]),
        )
        return Response(LeadDetailSerializer(updated_lead).data, status=status.HTTP_200_OK)


class InternalLeadDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, lead_id: str, *args, **kwargs):
        require_internal_service_token(request)
        lead = get_lead_by_id(lead_id)
        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_200_OK)


class InternalLeadWorkflowUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, lead_id: str, *args, **kwargs):
        require_internal_service_token(request)
        serializer = InternalLeadWorkflowUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            raise PermissionDenied("At least one workflow field must be provided")
        lead = get_lead_by_id(lead_id)
        updated_lead = update_lead_workflow_state(lead, cast(dict[str, object], serializer.validated_data))
        return Response(LeadDetailSerializer(updated_lead).data, status=status.HTTP_200_OK)