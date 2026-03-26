from __future__ import annotations

from unittest.mock import patch

from auth_lib import AuthContext, MembershipScope, TenantAccess
from django.test import Client, SimpleTestCase
from rest_framework.test import APITestCase

from apps.workflows.models import DeadLetterEvent, WorkflowRun


def build_auth_context(*, roles: list[str] | None = None) -> AuthContext:
    membership = MembershipScope(
        company_id="33333333-3333-3333-3333-333333333333",
        company_name="Acme",
        company_type="CHILD",
        parent_company_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        role="PARENT_ADMIN",
    )
    resolved_roles = roles or ["PARENT_ADMIN"]
    return AuthContext(
        token="valid-token",
        claims={
            "sub": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
            "roles": resolved_roles,
            "memberships": [membership.to_dict()],
            "tenant_access": {
                "membership_company_ids": [membership.company_id],
                "visible_company_ids": [membership.company_id],
                "data_company_ids": [membership.company_id],
                "parent_company_ids": [],
                "default_company_id": membership.company_id,
            },
        },
        subject="11111111-1111-1111-1111-111111111111",
        email="user@example.com",
        roles=resolved_roles,
        memberships=[membership],
        tenant_access=TenantAccess(
            membership_company_ids=(membership.company_id,),
            visible_company_ids=(membership.company_id,),
            data_company_ids=(membership.company_id,),
            parent_company_ids=tuple(),
            default_company_id=membership.company_id,
        ),
    )


class WorkflowHealthTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = Client().get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "workflow-service")


class WorkflowApiTests(APITestCase):
    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_list_workflow_runs_api(self, mock_build_auth_context):
        mock_build_auth_context.return_value = build_auth_context()
        WorkflowRun.objects.create(
            event_id="11111111-1111-1111-1111-111111111111",
            event_type="crm.lead.created",
            lead_id="22222222-2222-2222-2222-222222222222",
            company_id="33333333-3333-3333-3333-333333333333",
            status=WorkflowRun.Status.COMPLETED,
        )

        response = self.client.get("/api/v1/workflows/runs/", HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_workflow_run_detail_api(self, mock_build_auth_context):
        mock_build_auth_context.return_value = build_auth_context()
        workflow_run = WorkflowRun.objects.create(
            event_id="11111111-1111-1111-1111-111111111111",
            event_type="crm.lead.created",
            lead_id="22222222-2222-2222-2222-222222222222",
            company_id="33333333-3333-3333-3333-333333333333",
            status=WorkflowRun.Status.COMPLETED,
        )

        response = self.client.get(f"/api/v1/workflows/runs/{workflow_run.id}/", HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], str(workflow_run.id))

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_dead_letter_list_api(self, mock_build_auth_context):
        mock_build_auth_context.return_value = build_auth_context(roles=["PARENT_MANAGER"])
        DeadLetterEvent.objects.create(
            event_id="77777777-7777-7777-7777-777777777777",
            topic="crm.lead.created",
            event_type="crm.lead.created",
            payload={"event_id": "77777777-7777-7777-7777-777777777777", "payload": {}},
            error_message="boom",
        )

        response = self.client.get("/api/v1/workflows/dead-letters/", HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_dead_letter_list_requires_admin_role(self, mock_build_auth_context):
        mock_build_auth_context.return_value = build_auth_context(roles=["SALES_REP"])

        response = self.client.get("/api/v1/workflows/dead-letters/", HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 403)
