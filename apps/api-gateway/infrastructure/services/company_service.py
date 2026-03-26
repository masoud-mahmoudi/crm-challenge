from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrastructure.clients.identity_client import IdentityClient


@dataclass
class CompanyService:
    identity_client: IdentityClient

    def list_companies(self, *, token: str) -> list[dict[str, Any]]:
        response = self.identity_client.list_companies(token)
        return response if isinstance(response, list) else []

    def list_memberships(self, *, token: str) -> list[dict[str, Any]]:
        response = self.identity_client.list_memberships(token)
        return response if isinstance(response, list) else []