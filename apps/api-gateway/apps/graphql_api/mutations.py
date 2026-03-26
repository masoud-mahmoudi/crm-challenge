from __future__ import annotations

import strawberry

from apps.graphql_api.resolvers.activities import mutate_create_activity
from apps.graphql_api.resolvers.leads import mutate_assign_lead, mutate_create_lead, mutate_update_lead
from apps.graphql_api.types import Activity, CreateActivityInput, CreateLeadInput, Lead, UpdateLeadInput


@strawberry.type
class Mutation:
    create_lead: Lead = strawberry.mutation(resolver=mutate_create_lead, name="createLead")
    update_lead: Lead = strawberry.mutation(resolver=mutate_update_lead, name="updateLead")
    assign_lead: Lead = strawberry.mutation(resolver=mutate_assign_lead, name="assignLead")
    create_activity: Activity = strawberry.mutation(
        resolver=mutate_create_activity,
        name="createActivity",
    )