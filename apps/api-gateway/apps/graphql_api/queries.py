from __future__ import annotations

import strawberry

from apps.graphql_api.resolvers.activities import resolve_activities
from apps.graphql_api.resolvers.companies import resolve_companies, resolve_me
from apps.graphql_api.resolvers.leads import resolve_lead, resolve_leads
from apps.graphql_api.resolvers.workflow import resolve_workflow_runs
from apps.graphql_api.types import Activity, Company, Lead, MePayload, WorkflowRun


@strawberry.type
class Query:
    me: MePayload = strawberry.field(resolver=resolve_me)
    companies: list[Company] = strawberry.field(resolver=resolve_companies)
    leads: list[Lead] = strawberry.field(resolver=resolve_leads)
    lead: Lead = strawberry.field(resolver=resolve_lead)
    activities: list[Activity] = strawberry.field(resolver=resolve_activities)
    workflow_runs: list[WorkflowRun] = strawberry.field(resolver=resolve_workflow_runs, name="workflowRuns")