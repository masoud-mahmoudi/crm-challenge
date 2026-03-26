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

    def health(self, token: str | None = None):
        return self.get("/health", token=token)
