from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import Client, SimpleTestCase

from infrastructure.auth.context import RequestAuthContext


class GraphQLTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = Client()

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_me_query_success(self, mock_build_service_container: Mock, mock_build_auth_context: Mock) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["PARENT_ADMIN"],
            memberships=[],
            claims={
                "sub": "user-1",
                "email": "user@example.com",
                "tenant_access": {
                    "membership_company_ids": ["child-1"],
                    "visible_company_ids": ["parent-1", "child-1"],
                    "data_company_ids": ["child-1"],
                    "parent_company_ids": ["parent-1"],
                    "default_company_id": "child-1",
                },
            },
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.auth_service.me.return_value = {
            "user": {"id": "user-1", "email": "user@example.com", "full_name": "User One"},
            "memberships": [],
            "accessible_companies": [],
            "tenant_access": {"data_company_ids": ["child-1"]},
            "selected_company_id": "child-1",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps({"query": "query { me { user { id email fullName } } }"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["me"]["user"]["id"], "user-1")

    def test_leads_query_requires_auth(self) -> None:
        response = self.client.post(
            "/graphql",
            data=json.dumps({"query": "query { leads { id title } }"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_introspection_query_is_public(self) -> None:
        response = self.client.post(
            "/graphql",
            data=json.dumps(
                {
                    "operationName": "IntrospectionQuery",
                    "query": "query IntrospectionQuery { __schema { queryType { name } } }",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["__schema"]["queryType"]["name"], "Query")

    def test_introspection_get_sets_csrf_cookie(self) -> None:
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.get(
            "/graphql",
            data={
                "operationName": "IntrospectionQuery",
                "query": "query IntrospectionQuery { __schema { queryType { name } } }",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_leads_query_calls_crm_service(
        self,
        mock_build_service_container: Mock,
        mock_build_auth_context: Mock,
    ) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_MANAGER"],
            memberships=[],
            claims={
                "sub": "user-1",
                "email": "user@example.com",
                "tenant_access": {
                    "membership_company_ids": ["child-1"],
                    "visible_company_ids": ["child-1"],
                    "data_company_ids": ["child-1"],
                    "parent_company_ids": [],
                    "default_company_id": "child-1",
                },
            },
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.lead_service.list_leads.return_value = [
            {
                "id": "lead-1",
                "name": "Lead One",
                "email": "lead@example.com",
                "status": "NEW",
                "enrichment_status": "PENDING",
                "score": None,
                "company_id": "child-1",
                "owner_user_id": "user-1",
            }
        ]
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps({"query": "query { leads(status: \"NEW\", companyId: \"child-1\") { id title email companyId } }"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        mock_container.lead_service.list_leads.assert_called_once_with(
            token="valid-token",
            status="NEW",
            company_id="child-1",
        )
        self.assertEqual(response.json()["data"]["leads"][0]["title"], "Lead One")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_lead_query_calls_crm_service(
        self,
        mock_build_service_container: Mock,
        mock_build_auth_context: Mock,
    ) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_MANAGER"],
            memberships=[],
            claims={"sub": "user-1", "email": "user@example.com"},
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.lead_service.get_lead.return_value = {
            "id": "lead-1",
            "name": "Lead One",
            "status": "QUALIFIED",
            "company_id": "child-1",
            "owner_user_id": "user-1",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps({"query": "query { lead(leadId: \"lead-1\") { id title status } }"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        mock_container.lead_service.get_lead.assert_called_once_with(token="valid-token", lead_id="lead-1")
        self.assertEqual(response.json()["data"]["lead"]["status"], "QUALIFIED")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_create_lead_mutation_calls_crm_service(
        self,
        mock_build_service_container: Mock,
        mock_build_auth_context: Mock,
    ) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_MANAGER"],
            memberships=[],
            claims={
                "sub": "user-1",
                "email": "user@example.com",
                "tenant_access": {
                    "membership_company_ids": ["child-1"],
                    "visible_company_ids": ["child-1"],
                    "data_company_ids": ["child-1"],
                    "parent_company_ids": [],
                    "default_company_id": "child-1",
                },
            },
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.lead_service.create_lead.return_value = {
            "id": "lead-1",
            "title": "New Lead",
            "status": "NEW",
            "company_id": "company-1",
            "owner_user_id": "user-1",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps(
                {
                    "query": "mutation { createLead(input: { title: \"New Lead\", companyId: \"company-1\", ownerUserId: \"user-1\" }) { id title ownerUserId } }"
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        mock_container.lead_service.create_lead.assert_called_once()
        self.assertEqual(response.json()["data"]["createLead"]["id"], "lead-1")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_assign_lead_mutation_calls_crm_service(
        self,
        mock_build_service_container: Mock,
        mock_build_auth_context: Mock,
    ) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_MANAGER"],
            memberships=[],
            claims={"sub": "user-1", "email": "user@example.com"},
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.lead_service.assign_lead.return_value = {
            "id": "lead-1",
            "name": "Lead One",
            "status": "NEW",
            "company_id": "child-1",
            "owner_user_id": "user-2",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps(
                {
                    "query": "mutation { assignLead(leadId: \"lead-1\", ownerUserId: \"user-2\") { id ownerUserId } }"
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        mock_container.lead_service.assign_lead.assert_called_once_with(
            token="valid-token",
            lead_id="lead-1",
            owner_user_id="user-2",
        )
        self.assertEqual(response.json()["data"]["assignLead"]["ownerUserId"], "user-2")

    @patch("infrastructure.auth.middleware.build_auth_context_from_request")
    @patch("apps.graphql_api.context.build_service_container")
    def test_update_lead_mutation_calls_crm_service(
        self,
        mock_build_service_container: Mock,
        mock_build_auth_context: Mock,
    ) -> None:
        mock_build_auth_context.return_value = RequestAuthContext(
            token="valid-token",
            subject="user-1",
            email="user@example.com",
            roles=["SALES_MANAGER"],
            memberships=[],
            claims={"sub": "user-1", "email": "user@example.com"},
        )
        mock_container = SimpleNamespace(
            auth_service=Mock(),
            company_service=Mock(),
            lead_service=Mock(),
            activity_service=Mock(),
            workflow_service=Mock(),
        )
        mock_container.lead_service.update_lead.return_value = {
            "id": "lead-1",
            "name": "Updated Lead",
            "status": "QUALIFIED",
            "company_id": "child-1",
            "owner_user_id": "user-1",
        }
        mock_build_service_container.return_value = mock_container

        response = self.client.post(
            "/graphql",
            data=json.dumps(
                {
                    "query": "mutation { updateLead(leadId: \"lead-1\", input: { name: \"Updated Lead\", status: \"QUALIFIED\" }) { id title status } }"
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        self.assertEqual(response.status_code, 200)
        mock_container.lead_service.update_lead.assert_called_once_with(
            token="valid-token",
            lead_id="lead-1",
            payload={"name": "Updated Lead", "status": "QUALIFIED"},
        )
        self.assertEqual(response.json()["data"]["updateLead"]["title"], "Updated Lead")