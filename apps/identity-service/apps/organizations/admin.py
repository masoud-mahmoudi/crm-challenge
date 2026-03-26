from django.contrib import admin

from .models import Company, Membership


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "parent", "is_active", "created_at")
    list_filter = ("company_type", "is_active")
    search_fields = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "company__company_type")
    search_fields = ("user__email", "company__name")
