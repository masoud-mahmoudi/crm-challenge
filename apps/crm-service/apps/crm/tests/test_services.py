from __future__ import annotations

from unittest.mock import patch

from auth_lib import AuthContext, MembershipScope, TenantAccess
from django.test import TestCase
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.crm.models import Lead
from apps.crm.selectors import get_lead_for_user, list_leads_for_user
from apps.crm.services import assign_lead, create_lead
from apps.outbox.models import OutboxEvent


def build_auth_context(*, visible_company_ids: list[str], data_company_ids: list[str]) -> AuthContext:
    memberships = [MembershipScope(company_id=company_id, company_type="CHILD", role="SALES_MANAGER") for company_id in visible_company_ids]
    return AuthContext(
        token="token",
        claims={
            "sub": "33333333-3333-3333-3333-333333333333",
            "email": "user@example.com",
            "roles": ["SALES_MANAGER"],
            "memberships": [membership.to_dict() for membership in memberships],
            "tenant_access": {
                "membership_company_ids": visible_company_ids,
                "visible_company_ids": visible_company_ids,
                "data_company_ids": data_company_ids,
                "parent_company_ids": [],
                "default_company_id": data_company_ids[0] if data_company_ids else None,
            },
        },
        subject="33333333-3333-3333-3333-333333333333",
        email="user@example.com",
        roles=["SALES_MANAGER"],
        memberships=memberships,
        tenant_access=TenantAccess(
            membership_company_ids=tuple(visible_company_ids),
            visible_company_ids=tuple(visible_company_ids),
            data_company_ids=tuple(data_company_ids),
            parent_company_ids=tuple(),
            default_company_id=data_company_ids[0] if data_company_ids else None,
        ),
    )


class LeadServiceTests(TestCase):
    @patch("apps.crm.services.publish_outbox_event_by_id")
    def test_create_lead_creates_outbox_event(self, mock_publish_outbox_event_by_id):
        auth_context = build_auth_context(
            visible_company_ids=["11111111-1111-1111-1111-111111111111"],
            data_company_ids=["11111111-1111-1111-1111-111111111111"],
        )

        with self.captureOnCommitCallbacks(execute=True):
            lead = create_lead(
                auth_context,
                {
                    "company_id": "11111111-1111-1111-1111-111111111111",
                    "name": "Grace Hopper",
                    "email": "grace@example.com",
                },
            )

        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(OutboxEvent.objects.count(), 1)
        self.assertEqual(str(lead.company_id), "11111111-1111-1111-1111-111111111111")
        mock_publish_outbox_event_by_id.assert_called_once()
        self.assertEqual(
            mock_publish_outbox_event_by_id.call_args.args[0],
            str(OutboxEvent.objects.get().id),
        )

    def test_list_leads_respects_company_scope(self):
        auth_context = build_auth_context(
            visible_company_ids=["11111111-1111-1111-1111-111111111111"],
            data_company_ids=["11111111-1111-1111-1111-111111111111"],
        )
        Lead.objects.create(
            company_id="11111111-1111-1111-1111-111111111111",
            created_by_user_id="22222222-2222-2222-2222-222222222222",
            name="Visible",
        )
        Lead.objects.create(
            company_id="99999999-9999-9999-9999-999999999999",
            created_by_user_id="22222222-2222-2222-2222-222222222222",
            name="Hidden",
        )

        leads = list(list_leads_for_user(auth_context))
        self.assertEqual([lead.name for lead in leads], ["Visible"])

    def test_lead_detail_access_control(self):
        auth_context = build_auth_context(
            visible_company_ids=["11111111-1111-1111-1111-111111111111"],
            data_company_ids=["11111111-1111-1111-1111-111111111111"],
        )
        lead = Lead.objects.create(
            company_id="99999999-9999-9999-9999-999999999999",
            created_by_user_id="22222222-2222-2222-2222-222222222222",
            name="Hidden",
        )

        with self.assertRaises(PermissionDenied):
            get_lead_for_user(auth_context, str(lead.id))

        with self.assertRaises(NotFound):
            get_lead_for_user(auth_context, "11111111-1111-1111-1111-111111111111")

    def test_assign_lead(self):
        auth_context = build_auth_context(
            visible_company_ids=["11111111-1111-1111-1111-111111111111"],
            data_company_ids=["11111111-1111-1111-1111-111111111111"],
        )
        lead = Lead.objects.create(
            company_id="11111111-1111-1111-1111-111111111111",
            created_by_user_id="22222222-2222-2222-2222-222222222222",
            name="Assigned",
        )

        updated = assign_lead(auth_context, lead, "44444444-4444-4444-4444-444444444444")
        self.assertEqual(str(updated.owner_user_id), "44444444-4444-4444-4444-444444444444")