from __future__ import annotations

from auth_lib import AuthError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import cast

from infrastructure.auth.decorators import require_request_auth
from infrastructure.exceptions import ForbiddenError
from infrastructure.services import build_service_container

from .serializers import LoginSerializer, RefreshSerializer


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"service": "api-gateway", "status": "ok"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, str], serializer.validated_data)
        response_payload = build_service_container().auth_service.login(
            email=payload["email"],
            password=payload["password"],
        )
        return Response(response_payload, status=status.HTTP_200_OK)


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, str], serializer.validated_data)
        response_payload = build_service_container().auth_service.refresh(
            refresh_token=payload["refresh_token"],
        )
        return Response(response_payload, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = build_service_container().auth_service.logout()
        return Response(payload, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        auth_context = require_request_auth(request)
        selected_company_id = request.query_params.get("company_id")
        if selected_company_id:
            try:
                auth_context.require_company_access(selected_company_id)
            except AuthError as exc:
                raise ForbiddenError(str(exc)) from exc

        payload = build_service_container().auth_service.me(
            auth_context=auth_context,
            selected_company_id=selected_company_id,
        )
        return Response(payload, status=status.HTTP_200_OK)