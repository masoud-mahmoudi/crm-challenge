from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from auth_lib import filter_authorized_records

from infrastructure.auth.context import RequestAuthContext
from infrastructure.clients.identity_client import IdentityClient


@dataclass
class AuthService:
    identity_client: IdentityClient

    def login(self, *, email: str, password: str) -> dict[str, Any]:
        payload = self.identity_client.login(email=email, password=password)
        return self._normalize_token_response(payload)

    def refresh(self, *, refresh_token: str) -> dict[str, Any]:
        payload = self.identity_client.refresh(refresh_token=refresh_token)
        return self._normalize_token_response(payload)

    def logout(self) -> dict[str, Any]:
        return {
            "success": True,
            "detail": "Logout is a client-side no-op until token revocation is introduced upstream.",
        }

    def me(
        self,
        *,
        auth_context: RequestAuthContext,
        selected_company_id: str | None = None,
    ) -> dict[str, Any]:
        token = auth_context.token
        user_payload = self.identity_client.me(token)
        memberships = self.identity_client.list_memberships(token)
        accessible_companies = self.identity_client.list_companies(token)

        memberships = [
            membership
            for membership in memberships
            if isinstance(membership, dict)
            and isinstance(membership.get("company"), dict)
            and auth_context.can_access_company(str(membership["company"].get("id", "")), data_scope=False)
        ]
        accessible_companies = filter_authorized_records(
            auth_context,
            [company for company in accessible_companies if isinstance(company, dict)],
            company_id_field="id",
            data_scope=False,
        )

        if selected_company_id:
            memberships = [
                membership
                for membership in memberships
                if str((membership.get("company") or {}).get("id")) == selected_company_id
            ]
            accessible_companies = [
                company for company in accessible_companies if str(company.get("id")) == selected_company_id
            ]

        user_payload.setdefault("id", auth_context.subject)
        user_payload.setdefault("email", auth_context.email)
        return {
            "user": user_payload,
            "memberships": memberships,
            "accessible_companies": accessible_companies,
            "tenant_access": auth_context.tenant_access.to_dict(),
            "selected_company_id": selected_company_id or auth_context.tenant_access.default_company_id,
        }

    @staticmethod
    def _normalize_token_response(payload: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "access_token": payload.get("access_token"),
            "token_type": payload.get("token_type", "Bearer"),
            "expires_in": payload.get("expires_in"),
        }
        if payload.get("refresh_token") is not None:
            normalized["refresh_token"] = payload.get("refresh_token")
        if payload.get("user") is not None:
            normalized["user"] = payload.get("user")
        return normalized