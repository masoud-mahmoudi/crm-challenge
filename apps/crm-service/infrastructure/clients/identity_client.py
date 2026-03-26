from __future__ import annotations

from django.conf import settings
import httpx


class IdentityClient:
    def __init__(self) -> None:
        self.base_url = settings.IDENTITY_SERVICE_BASE_URL.rstrip("/")

    def get_current_user_companies(self, token: str):
        response = httpx.get(
            f"{self.base_url}/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()