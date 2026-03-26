from __future__ import annotations

import logging
from typing import Any

import httpx

from infrastructure.exceptions import (
    DownstreamServiceError,
    ForbiddenError,
    ServiceUnavailableError,
    UnauthorizedError,
)


logger = logging.getLogger(__name__)


class BaseHTTPClient:
    def __init__(self, *, service_name: str, base_url: str, timeout: float) -> None:
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _send(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        return httpx.request(method, url, timeout=self.timeout, **kwargs)

    def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = self._send(method, url, headers=headers, json=json_body, params=params)
        except httpx.RequestError as exc:
            logger.warning("Downstream %s request failed: %s", self.service_name, exc)
            raise ServiceUnavailableError(f"{self.service_name} is unavailable") from exc

        payload = self._parse_payload(response)
        if response.is_success:
            return payload

        self._raise_for_error(response.status_code, payload)

    def get(self, path: str, *, token: str | None = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, token=token, params=params)

    def post(self, path: str, *, token: str | None = None, json_body: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, token=token, json_body=json_body)

    def _parse_payload(self, response: httpx.Response) -> Any:
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"detail": response.text}

    def _raise_for_error(self, status_code: int, payload: Any) -> None:
        detail = self._extract_message(payload)
        if status_code == 401:
            raise UnauthorizedError(detail or f"{self.service_name} rejected the bearer token", details=payload)
        if status_code == 403:
            raise ForbiddenError(detail or f"Access denied by {self.service_name}", details=payload)
        if status_code >= 500:
            logger.error("%s upstream returned %s: %s", self.service_name, status_code, payload)
            raise DownstreamServiceError(
                detail or f"{self.service_name} failed to process the request",
                status_code=502,
                code="downstream_error",
                details=payload,
            )

        raise DownstreamServiceError(
            detail or f"{self.service_name} request failed",
            status_code=status_code,
            code="downstream_error",
            details=payload,
        )

    @staticmethod
    def _extract_message(payload: Any) -> str | None:
        if isinstance(payload, dict):
            for key in ("detail", "error", "message"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
                if isinstance(value, dict):
                    nested = BaseHTTPClient._extract_message(value)
                    if nested:
                        return nested
        return None