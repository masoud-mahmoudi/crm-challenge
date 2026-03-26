from __future__ import annotations

from typing import Any


class GatewayError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        code: str = "gateway_error",
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.details = details


class UnauthorizedError(GatewayError):
    def __init__(self, message: str = "Authentication failed", *, details: Any | None = None) -> None:
        super().__init__(message, status_code=401, code="unauthorized", details=details)


class ForbiddenError(GatewayError):
    def __init__(self, message: str = "Forbidden", *, details: Any | None = None) -> None:
        super().__init__(message, status_code=403, code="forbidden", details=details)


class DownstreamServiceError(GatewayError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 502,
        code: str = "downstream_error",
        details: Any | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, code=code, details=details)


class ServiceUnavailableError(DownstreamServiceError):
    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__(message, status_code=503, code="service_unavailable", details=details)