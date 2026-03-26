from __future__ import annotations

import time
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from auth_lib import generate_rsa_key_pair
from infrastructure.auth.adapters import build_auth_context_from_headers
from infrastructure.exceptions import UnauthorizedError

import jwt


class _FakeSigningKey:
    def __init__(self, key: str) -> None:
        self.key = key


class _FakeJWKClient:
    def __init__(self, key: str) -> None:
        self.key = key

    def get_signing_key_from_jwt(self, token: str) -> _FakeSigningKey:
        return _FakeSigningKey(self.key)


@override_settings(
    JWT_JWKS_URL="https://jwks.example.local",
    JWT_ISSUER="identity-service",
    JWT_AUDIENCE="crm-platform",
)
class TokenValidationTests(SimpleTestCase):
    def setUp(self) -> None:
        self.key_pair = generate_rsa_key_pair(kid="gateway-test")
        self.jwk_client = _FakeJWKClient(self.key_pair["public_key_pem"])

    def _encode_token(self, *, issuer: str = "identity-service", audience: str = "crm-platform", exp_offset: int = 300) -> str:
        now = int(time.time())
        return jwt.encode(
            {
                "iss": issuer,
                "aud": audience,
                "sub": "user-1",
                "email": "user@example.com",
                "roles": ["PARENT_ADMIN"],
                "memberships": [
                    {
                        "company_id": "parent-1",
                        "company_name": "Acme Group",
                        "company_type": "PARENT",
                        "parent_company_id": None,
                        "role": "PARENT_ADMIN",
                    }
                ],
                "tenant_access": {
                    "membership_company_ids": ["parent-1"],
                    "visible_company_ids": ["parent-1", "child-1", "child-2"],
                    "data_company_ids": ["child-1", "child-2"],
                    "parent_company_ids": ["parent-1"],
                    "default_company_id": "child-1",
                },
                "iat": now,
                "exp": now + exp_offset,
            },
            self.key_pair["private_key_pem"],
            algorithm="RS256",
            headers={"kid": self.key_pair["kid"]},
        )

    @patch("auth_lib._get_jwks_client")
    def test_valid_token_accepted(self, mock_get_jwks_client) -> None:
        mock_get_jwks_client.return_value = self.jwk_client
        auth_context = build_auth_context_from_headers({"Authorization": f"Bearer {self._encode_token()}"})
        self.assertEqual(auth_context.user_id, "user-1")
        self.assertTrue(auth_context.can_access_company("child-1"))
        self.assertFalse(auth_context.can_access_company("parent-1"))

    @patch("auth_lib._get_jwks_client")
    def test_expired_token_rejected(self, mock_get_jwks_client) -> None:
        mock_get_jwks_client.return_value = self.jwk_client
        with self.assertRaises(UnauthorizedError):
            build_auth_context_from_headers({"Authorization": f"Bearer {self._encode_token(exp_offset=-10)}"})

    @patch("auth_lib._get_jwks_client")
    def test_wrong_issuer_or_audience_rejected(self, mock_get_jwks_client) -> None:
        mock_get_jwks_client.return_value = self.jwk_client
        with self.assertRaises(UnauthorizedError):
            build_auth_context_from_headers(
                {"Authorization": f"Bearer {self._encode_token(issuer='wrong-issuer', audience='wrong-audience')}"}
            )