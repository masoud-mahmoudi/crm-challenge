from __future__ import annotations

from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "company_id",
        "owner_user_id",
        "status",
        "enrichment_status",
        "created_at",
    )
    list_filter = ("status", "enrichment_status")
    search_fields = ("name", "email", "company_id", "owner_user_id")
    readonly_fields = ("id", "created_at", "updated_at")