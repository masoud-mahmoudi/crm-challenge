from __future__ import annotations

from django.test import TestCase

from apps.crm.models import Lead


class LeadModelTests(TestCase):
    def test_lead_creation(self):
        lead = Lead.objects.create(
            company_id="11111111-1111-1111-1111-111111111111",
            created_by_user_id="22222222-2222-2222-2222-222222222222",
            name="Ada Lovelace",
        )
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.enrichment_status, Lead.EnrichmentStatus.PENDING)