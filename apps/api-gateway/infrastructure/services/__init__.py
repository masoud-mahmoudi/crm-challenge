from __future__ import annotations

from dataclasses import dataclass

from infrastructure.clients.crm_client import CRMClient
from infrastructure.clients.identity_client import IdentityClient
from infrastructure.clients.workflow_client import WorkflowClient

from .activity_service import ActivityService
from .auth_service import AuthService
from .company_service import CompanyService
from .lead_service import LeadService
from .workflow_service import WorkflowService


@dataclass(frozen=True)
class ServiceContainer:
    auth_service: AuthService
    company_service: CompanyService
    lead_service: LeadService
    activity_service: ActivityService
    workflow_service: WorkflowService


def build_service_container() -> ServiceContainer:
    identity_client = IdentityClient()
    crm_client = CRMClient()
    workflow_client = WorkflowClient()
    return ServiceContainer(
        auth_service=AuthService(identity_client=identity_client),
        company_service=CompanyService(identity_client=identity_client),
        lead_service=LeadService(crm_client=crm_client),
        activity_service=ActivityService(crm_client=crm_client),
        workflow_service=WorkflowService(workflow_client=workflow_client),
    )


__all__ = ["ServiceContainer", "build_service_container"]