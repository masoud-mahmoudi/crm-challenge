from __future__ import annotations

import logging
from typing import Any

import httpx

from apps.workflows.exceptions import DownstreamServiceError


logger = logging.getLogger(__name__)


class BaseHTTPClient:
    def __init__(self, *, service_name: str, base_url: str, timeout: float) -> None:
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

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
            response = httpx.request(method, url, headers=headers, json=json_body, params=params, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise DownstreamServiceError(f"{self.service_name} is unavailable") from exc

        payload = self._parse_payload(response)
        if response.is_success:
            return payload

        logger.warning("Downstream %s returned %s: %s", self.service_name, response.status_code, payload)
        raise DownstreamServiceError(
            self._extract_message(payload) or f"{self.service_name} request failed",
            status_code=response.status_code,
            payload=payload,
        )

    def get(self, path: str, *, token: str | None = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, token=token, params=params)

    def post(self, path: str, *, token: str | None = None, json_body: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, token=token, json_body=json_body)

    @staticmethod
    def _parse_payload(response: httpx.Response) -> Any:
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"detail": response.text}

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
