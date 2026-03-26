from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from infrastructure.db.models import TimeStampedModel, UUIDPrimaryKeyModel


class Company(UUIDPrimaryKeyModel, TimeStampedModel):
    class CompanyType(models.TextChoices):
        PARENT = "PARENT", "Parent"
        CHILD = "CHILD", "Child"

    name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=16, choices=CompanyType.choices)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.PROTECT,
    )
    is_active = models.BooleanField(default=True)

    class Meta(UUIDPrimaryKeyModel.Meta, TimeStampedModel.Meta):
        ordering = ("name",)

    def clean(self):
        super().clean()
        if self.company_type == self.CompanyType.PARENT and self.parent is not None:
            raise ValidationError({"parent": "Parent companies cannot have a parent company."})
        if self.company_type == self.CompanyType.CHILD and self.parent is None:
            raise ValidationError({"parent": "Child companies must reference a parent company."})
        if self.company_type == self.CompanyType.CHILD and self.parent and self.parent.company_type != self.CompanyType.PARENT:
            raise ValidationError({"parent": "Child companies must reference a parent company of type PARENT."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Membership(UUIDPrimaryKeyModel, TimeStampedModel):
    class Role(models.TextChoices):
        PARENT_ADMIN = "PARENT_ADMIN", "Parent admin"
        PARENT_MANAGER = "PARENT_MANAGER", "Parent manager"
        CHILD_ADMIN = "CHILD_ADMIN", "Child admin"
        SALES_MANAGER = "SALES_MANAGER", "Sales manager"
        SALES_REP = "SALES_REP", "Sales rep"
        VIEWER = "VIEWER", "Viewer"

    user = models.ForeignKey("accounts.User", related_name="memberships", on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name="memberships", on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta(UUIDPrimaryKeyModel.Meta, TimeStampedModel.Meta):
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(fields=("user", "company", "role"), name="unique_user_company_role"),
        ]

    @property
    def parent_roles(self) -> set[str]:
        return {self.Role.PARENT_ADMIN, self.Role.PARENT_MANAGER}

    @property
    def child_roles(self) -> set[str]:
        return {self.Role.CHILD_ADMIN, self.Role.SALES_MANAGER, self.Role.SALES_REP, self.Role.VIEWER}

    def clean(self):
        super().clean()
        if self.company.company_type == Company.CompanyType.PARENT and self.role not in self.parent_roles:
            raise ValidationError({"role": "Only parent roles can be assigned to parent companies."})
        if self.company.company_type == Company.CompanyType.CHILD and self.role not in self.child_roles:
            raise ValidationError({"role": "Only child roles can be assigned to child companies."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.company.name} ({self.role})"
