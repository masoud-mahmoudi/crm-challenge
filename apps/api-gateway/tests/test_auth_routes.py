from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import Client, SimpleTestCase

from infrastructure.auth.context import RequestAuthContext


class AuthRouteTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = Client()

    @patch("apps.rest_api.views.build_service_container")
    def test_login_success(self, mock_build_service_container: Mock) -> None:
        mock_container = SimpleNamespace(auth_service=Mock())
        mock_container.auth_service.login.return_value = {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "token_type": "Bearer",
            "expires_in": 900,
            "user": {"id": "user-1", "email": "user@example.com"},
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/api/auth/login",
            data={"email": "user@example.com", "password": "secret"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "access-token")

    @patch("apps.rest_api.views.build_service_container")
    def test_refresh_success(self, mock_build_service_container: Mock) -> None:
        mock_container = SimpleNamespace(auth_service=Mock())
        mock_container.auth_service.refresh.return_value = {
            "access_token": "new-access-token",
            "token_type": "Bearer",
            "expires_in": 900,
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/api/auth/refresh",
            data={"refresh_token": "refresh-token"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "new-access-token")

    def test_me_requires_auth(self) -> None:
        response = self.client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_invalid_token_returns_401(self, mock_build_auth_context: Mock) -> None:
        from infrastructure.exceptions import UnauthorizedError

        mock_build_auth_context.side_effect = UnauthorizedError("Invalid token")

        response = self.client.get("/api/auth/me", HTTP_AUTHORIZATION="Bearer invalid-token")
        self.assertEqual(response.status_code, 401)

    @patch("apps.rest_api.views.build_service_container")
    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_me_returns_profile(self, mock_build_auth_context: Mock, mock_build_service_container: Mock) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["PARENT_ADMIN"],
            memberships=[],
            claims={
                "sub": "user-1",
                "email": "user@example.com",
                "tenant_access": {
                    "membership_company_ids": ["child-1"],
                    "visible_company_ids": ["child-1"],
                    "data_company_ids": ["child-1"],
                    "parent_company_ids": [],
                    "default_company_id": "child-1",
                },
            },
        )
        mock_container = SimpleNamespace(auth_service=Mock())
        mock_container.auth_service.me.return_value = {
            "user": {"id": "user-1", "email": "user@example.com"},
            "memberships": [],
            "accessible_companies": [],
            "tenant_access": {"data_company_ids": ["child-1"]},
            "selected_company_id": "child-1",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.get("/api/auth/me", HTTP_AUTHORIZATION="Bearer valid-token")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["id"], "user-1")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_me_rejects_unauthorized_company_scope(self, mock_build_auth_context: Mock) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_REP"],
            memberships=[],
            claims={
                "sub": "user-1",
                "email": "user@example.com",
                "tenant_access": {
                    "membership_company_ids": ["child-1"],
                    "visible_company_ids": ["child-1"],
                    "data_company_ids": ["child-1"],
                    "parent_company_ids": [],
                    "default_company_id": "child-1",
                },
            },
        )

        response = self.client.get(
            "/api/auth/me?company_id=child-2",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )
        self.assertEqual(response.status_code, 403)