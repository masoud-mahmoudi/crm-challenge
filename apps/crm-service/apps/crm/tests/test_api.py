from __future__ import annotations

from unittest.mock import patch

from auth_lib import AuthContext, MembershipScope, TenantAccess
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.crm.models import Lead


TORONTO_COMPANY_ID = "11111111-1111-1111-1111-111111111111"
MONTREAL_COMPANY_ID = "22222222-2222-2222-2222-222222222222"
GROUP_COMPANY_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
OTHER_COMPANY_ID = "99999999-9999-9999-9999-999999999999"


def build_auth_context(
    *,
    membership_company_id: str = TORONTO_COMPANY_ID,
    membership_company_name: str = "Acme Toronto",
    membership_company_type: str = "CHILD",
    parent_company_id: str | None = GROUP_COMPANY_ID,
    visible_company_ids: list[str] | None = None,
    data_company_ids: list[str] | None = None,
    parent_company_ids: list[str] | None = None,
) -> AuthContext:
    membership = MembershipScope(
        company_id=membership_company_id,
        company_name=membership_company_name,
        company_type=membership_company_type,
        parent_company_id=parent_company_id,
        role="SALES_MANAGER",
    )
    visible_company_ids = visible_company_ids or [membership.company_id]
    data_company_ids = data_company_ids if data_company_ids is not None else [membership.company_id]
    parent_company_ids = parent_company_ids if parent_company_ids is not None else []

    return AuthContext(
        token="valid-token",
        claims={
            "sub": "33333333-3333-3333-3333-333333333333",
            "email": "user@example.com",
            "roles": ["SALES_MANAGER"],
            "memberships": [membership.to_dict()],
            "tenant_access": {
                "membership_company_ids": [membership.company_id],
                "visible_company_ids": visible_company_ids,
                "data_company_ids": data_company_ids,
                "parent_company_ids": parent_company_ids,
                "default_company_id": data_company_ids[0] if data_company_ids else None,
            },
        },
        subject="33333333-3333-3333-3333-333333333333",
        email="user@example.com",
        roles=["SALES_MANAGER"],
        memberships=[membership],
        tenant_access=TenantAccess(
            membership_company_ids=(membership.company_id,),
            visible_company_ids=tuple(visible_company_ids),
            data_company_ids=tuple(data_company_ids),
            parent_company_ids=tuple(parent_company_ids),
            default_company_id=data_company_ids[0] if data_company_ids else None,
        ),
    )


class LeadApiTests(APITestCase):
    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_create_lead_endpoint(self, mock_auth):
        mock_auth.return_value = build_auth_context()
        response = self.client.post(
            reverse("lead-list-create"),
            {
                "company_id": TORONTO_COMPANY_ID,
                "name": "API Lead",
                "email": "api@example.com",
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "API Lead")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_parent_company_user_cannot_create_lead(self, mock_auth):
        mock_auth.return_value = build_auth_context(
            membership_company_id=GROUP_COMPANY_ID,
            membership_company_name="Acme Group",
            membership_company_type="PARENT",
            parent_company_id=None,
            visible_company_ids=[GROUP_COMPANY_ID],
            data_company_ids=[],
            parent_company_ids=[GROUP_COMPANY_ID],
        )

        response = self.client.post(
            reverse("lead-list-create"),
            {
                "company_id": GROUP_COMPANY_ID,
                "name": "Forbidden Parent Lead",
                "email": "parent@example.com",
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Lead.objects.count(), 0)

    def test_missing_auth_returns_401(self):
        response = self.client.get(reverse("lead-list-create"))
        self.assertEqual(response.status_code, 401)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_health_endpoint(self, mock_auth):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_lead_detail_requires_scope(self, mock_auth):
        mock_auth.return_value = build_auth_context()
        lead = Lead.objects.create(
            company_id=OTHER_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Hidden",
        )
        response = self.client.get(reverse("lead-detail", kwargs={"lead_id": lead.id}), HTTP_AUTHORIZATION="Bearer valid-token")
        self.assertEqual(response.status_code, 403)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_toronto_user_cannot_read_montreal_lead(self, mock_auth):
        mock_auth.return_value = build_auth_context(
            membership_company_id=TORONTO_COMPANY_ID,
            membership_company_name="Acme Toronto",
            membership_company_type="CHILD",
            parent_company_id=GROUP_COMPANY_ID,
            visible_company_ids=[TORONTO_COMPANY_ID],
            data_company_ids=[TORONTO_COMPANY_ID],
            parent_company_ids=[],
        )
        montreal_lead = Lead.objects.create(
            company_id=MONTREAL_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Montreal Lead",
        )

        response = self.client.get(
            reverse("lead-detail", kwargs={"lead_id": montreal_lead.id}),
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 403)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_list_leads_only_returns_accessible_company_leads(self, mock_auth):
        mock_auth.return_value = build_auth_context(
            visible_company_ids=[TORONTO_COMPANY_ID],
            data_company_ids=[TORONTO_COMPANY_ID],
        )
        visible_lead = Lead.objects.create(
            company_id=TORONTO_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Visible Lead",
        )
        Lead.objects.create(
            company_id=OTHER_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Hidden Lead",
        )

        response = self.client.get(reverse("lead-list-create"), HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(visible_lead.id))
        self.assertEqual(response.data[0]["name"], "Visible Lead")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_parent_manager_can_read_toronto_and_montreal_leads(self, mock_auth):
        mock_auth.return_value = build_auth_context(
            membership_company_id=GROUP_COMPANY_ID,
            membership_company_name="Acme Group",
            membership_company_type="PARENT",
            parent_company_id=None,
            visible_company_ids=[GROUP_COMPANY_ID, TORONTO_COMPANY_ID, MONTREAL_COMPANY_ID],
            data_company_ids=[TORONTO_COMPANY_ID, MONTREAL_COMPANY_ID],
            parent_company_ids=[GROUP_COMPANY_ID],
        )
        toronto_lead = Lead.objects.create(
            company_id=TORONTO_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Toronto Lead",
        )
        montreal_lead = Lead.objects.create(
            company_id=MONTREAL_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Montreal Lead",
        )
        Lead.objects.create(
            company_id=OTHER_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Other Lead",
        )

        response = self.client.get(reverse("lead-list-create"), HTTP_AUTHORIZATION="Bearer valid-token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {lead["id"] for lead in response.data},
            {str(toronto_lead.id), str(montreal_lead.id)},
        )
        self.assertEqual(
            {lead["name"] for lead in response.data},
            {"Toronto Lead", "Montreal Lead"},
        )

    def test_internal_lead_detail_requires_service_token(self):
        lead = Lead.objects.create(
            company_id=TORONTO_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Internal Lead",
            email="internal@example.com",
        )

        response = self.client.get(
            reverse("internal-lead-detail", kwargs={"lead_id": lead.id}),
            HTTP_AUTHORIZATION="Bearer wrong-token",
        )

        self.assertEqual(response.status_code, 401)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    def test_internal_workflow_update_with_service_token(self, mock_auth):
        lead = Lead.objects.create(
            company_id=TORONTO_COMPANY_ID,
            created_by_user_id="33333333-3333-3333-3333-333333333333",
            name="Internal Lead",
        )

        with self.settings(INTERNAL_SERVICE_TOKEN="internal-token"):
            response = self.client.post(
                reverse("internal-lead-workflow-update", kwargs={"lead_id": lead.id}),
                {
                    "enrichment_status": Lead.EnrichmentStatus.COMPLETED,
                    "score": 85,
                    "status": Lead.Status.QUALIFIED,
                },
                format="json",
                HTTP_AUTHORIZATION="Bearer internal-token",
            )

        lead.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(lead.score, 85)
        self.assertEqual(lead.enrichment_status, Lead.EnrichmentStatus.COMPLETED)
