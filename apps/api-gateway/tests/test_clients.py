from __future__ import annotations

from unittest.mock import patch

import httpx
from django.test import SimpleTestCase, override_settings

from infrastructure.clients.crm_client import CRMClient
from infrastructure.clients.identity_client import IdentityClient
from infrastructure.exceptions import DownstreamServiceError


@override_settings(
    IDENTITY_SERVICE_BASE_URL="http://identity-service:8001",
    CRM_SERVICE_BASE_URL="http://crm-service:8002",
    REQUEST_TIMEOUT_SECONDS=5,
)
class ClientTests(SimpleTestCase):
    @patch("httpx.request")
    def test_downstream_200_mapping(self, mock_request) -> None:
        request = httpx.Request("POST", "http://identity-service:8001/api/v1/auth/login/")
        mock_request.return_value = httpx.Response(
            200,
            json={"access_token": "token"},
            request=request,
        )

        payload = IdentityClient().login(email="user@example.com", password="secret")
        self.assertEqual(payload["access_token"], "token")

    @patch("httpx.request")
    def test_downstream_error_mapping(self, mock_request) -> None:
        request = httpx.Request("GET", "http://crm-service:8002/api/v1/leads/")
        mock_request.return_value = httpx.Response(
            500,
            json={"detail": "boom"},
            request=request,
        )

        with self.assertRaises(DownstreamServiceError):
            CRMClient().list_leads("token")