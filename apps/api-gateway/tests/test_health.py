from __future__ import annotations

from django.test import Client, SimpleTestCase


class HealthTests(SimpleTestCase):
    def test_health(self) -> None:
        response = Client().get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "api-gateway")

    def test_health_preflight_returns_cors_headers(self) -> None:
        response = Client().options(
            "/api/health",
            HTTP_ORIGIN="http://localhost:4200",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:4200")