from __future__ import annotations

from django.conf import settings

from .base import BaseHTTPClient


class IdentityClient(BaseHTTPClient):
    def __init__(self) -> None:
        super().__init__(
            service_name="identity-service",
            base_url=settings.IDENTITY_SERVICE_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )

    def login(self, email: str, password: str):
        return self.post("/api/v1/auth/login/", json_body={"email": email, "password": password})

    def refresh(self, refresh_token: str):
        return self.post("/api/v1/auth/refresh/", json_body={"refresh_token": refresh_token})

    def me(self, token: str):
        return self.get("/api/v1/users/me/", token=token)

    def list_companies(self, token: str):
        return self.get("/api/v1/companies/", token=token)

    def list_memberships(self, token: str):
        return self.get("/api/v1/memberships/", token=token)