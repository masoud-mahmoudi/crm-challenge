from __future__ import annotations

from typing import Any

import strawberry


@strawberry.type
class Company:
    id: strawberry.ID
    name: str
    company_type: str
    parent_id: str | None
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Company":
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            company_type=str(data.get("company_type", "")),
            parent_id=str(data.get("parent_id")) if data.get("parent_id") else None,
            is_active=bool(data.get("is_active", True)),
            created_at=str(data.get("created_at")) if data.get("created_at") else None,
            updated_at=str(data.get("updated_at")) if data.get("updated_at") else None,
        )


@strawberry.type
class Membership:
    id: strawberry.ID
    role: str
    is_active: bool
    company: Company
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Membership":
        return cls(
            id=str(data.get("id", "")),
            role=str(data.get("role", "")),
            is_active=bool(data.get("is_active", True)),
            company=Company.from_dict(data.get("company") or {}),
            created_at=str(data.get("created_at")) if data.get("created_at") else None,
            updated_at=str(data.get("updated_at")) if data.get("updated_at") else None,
        )


@strawberry.type
class User:
    id: strawberry.ID
    email: str
    full_name: str | None
    is_active: bool = True
    is_staff: bool = False
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(
            id=str(data.get("id", "")),
            email=str(data.get("email", "")),
            full_name=str(data.get("full_name")) if data.get("full_name") else None,
            is_active=bool(data.get("is_active", True)),
            is_staff=bool(data.get("is_staff", False)),
            created_at=str(data.get("created_at")) if data.get("created_at") else None,
        )


@strawberry.type
class Lead:
    id: strawberry.ID
    title: str
    name: str | None = None
    status: str
    company_id: str | None
    owner_user_id: str | None
    source: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    enrichment_status: str | None = None
    score: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lead":
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", data.get("name", ""))),
            name=str(data.get("name", data.get("title", ""))) if (data.get("name") or data.get("title")) else None,
            status=str(data.get("status", "")),
            company_id=str(data.get("company_id")) if data.get("company_id") else None,
            owner_user_id=str(data.get("owner_user_id")) if data.get("owner_user_id") else None,
            source=str(data.get("source")) if data.get("source") else None,
            description=str(data.get("description")) if data.get("description") else None,
            email=str(data.get("email")) if data.get("email") else None,
            phone=str(data.get("phone")) if data.get("phone") else None,
            enrichment_status=str(data.get("enrichment_status")) if data.get("enrichment_status") else None,
            score=int(data.get("score")) if data.get("score") is not None else None,
            created_at=str(data.get("created_at")) if data.get("created_at") else None,
            updated_at=str(data.get("updated_at")) if data.get("updated_at") else None,
        )


@strawberry.type
class Activity:
    id: strawberry.ID
    type: str
    summary: str
    lead_id: str | None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Activity":
        return cls(
            id=str(data.get("id", "")),
            type=str(data.get("type", "")),
            summary=str(data.get("summary", "")),
            lead_id=str(data.get("lead_id")) if data.get("lead_id") else None,
            created_at=str(data.get("created_at")) if data.get("created_at") else None,
        )


@strawberry.type
class WorkflowRun:
    id: strawberry.ID
    workflow_name: str
    status: str
    started_at: str | None = None
    finished_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowRun":
        return cls(
            id=str(data.get("id", "")),
            workflow_name=str(data.get("workflow_name", data.get("name", ""))),
            status=str(data.get("status", "")),
            started_at=str(data.get("started_at")) if data.get("started_at") else None,
            finished_at=str(data.get("finished_at")) if data.get("finished_at") else None,
        )


@strawberry.type
class MePayload:
    user: User
    memberships: list[Membership]
    accessible_companies: list[Company]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MePayload":
        return cls(
            user=User.from_dict(data.get("user") or {}),
            memberships=[Membership.from_dict(item) for item in data.get("memberships") or []],
            accessible_companies=[Company.from_dict(item) for item in data.get("accessible_companies") or []],
        )


@strawberry.input
class CreateLeadInput:
    name: str | None = None
    title: str | None = None
    company_id: str
    owner_user_id: str | None = None
    source: str | None = None
    email: str | None = None
    phone: str | None = None


@strawberry.input
class UpdateLeadInput:
    name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str | None = None
    status: str | None = None


@strawberry.input
class CreateActivityInput:
    lead_id: str
    type: str
    summary: str