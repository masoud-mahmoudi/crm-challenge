from __future__ import annotations

from rest_framework.permissions import BasePermission


ADMIN_ROLES = {"PARENT_ADMIN", "PARENT_MANAGER"}


class IsAuthenticatedWorkflowUser(BasePermission):
    message = "Authentication credentials were not provided."

    def has_permission(self, request, view):
        return getattr(request, "auth_context", None) is not None


class IsWorkflowAdmin(BasePermission):
    message = "Admin role required."

    def has_permission(self, request, view):
        auth_context = getattr(request, "auth_context", None)
        if auth_context is None:
            return False
        return bool(set(getattr(auth_context, "roles", [])) & ADMIN_ROLES)
