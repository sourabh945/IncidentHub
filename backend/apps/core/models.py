"""
apps/core/models.py

Shared abstract base models. None of these create tables by themselves.

Pick the base class for each concrete model:

    Organization            UUIDModel, TimeStampedModel, SoftDeleteMixin
    User                    UUIDModel, TimeStampedModel  (+ AbstractBaseUser)
    Membership, Team,
    TeamMembership,
    Invitation, Environment,
    OrganizationSettings,
    AuditLog                OrgScopedModel               (hard delete)
    Anything tenant-owned
    that must be recoverable OrgScopedSoftDeleteModel

AuditLog must stay append-only, so never give it soft delete.
"""

import uuid

from django.db import models
from django.utils import timezone


# --------------------------------------------------------------------
# Basic building blocks
# --------------------------------------------------------------------

class UUIDModel(models.Model):
    """Random UUID primary key instead of 1, 2, 3 (not guessable in URLs)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """created_at and updated_at, maintained automatically."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# --------------------------------------------------------------------
# Soft delete
# --------------------------------------------------------------------

class SoftDeleteQuerySet(models.QuerySet):
    """
    Queryset helpers for soft delete.

    active()    rows that are not deleted
    deleted()   rows that are deleted
    delete()    SOFT delete every row in the queryset
    restore()   undo a soft delete
    hard_delete()  really remove the rows from the database
    """

    def active(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return self.update(deleted_at=timezone.now())

    def restore(self):
        return self.update(deleted_at=None)

    def hard_delete(self):
        return super().delete()

    # queryset_only keeps these OFF the manager. Without it,
    # Model.objects.delete() would soft delete the whole table.
    delete.queryset_only = True
    restore.queryset_only = True
    hard_delete.queryset_only = True


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Default manager: deleted rows are hidden."""

    def get_queryset(self):
        return super().get_queryset().active()


class SoftDeleteMixin(models.Model):
    """
    Marks a row deleted with a timestamp instead of removing it.

        Model.objects                    -> only active rows
        Model.all_objects                -> every row
        Model.all_objects.deleted()      -> only deleted rows
    """

    deleted_at = models.DateTimeField(
        null=True, blank=True, editable=False, db_index=True
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


# --------------------------------------------------------------------
# Organization scoping (multi-tenancy)
# --------------------------------------------------------------------

class OrgScopedQuerySet(models.QuerySet):
    def for_org(self, org):
        return self.filter(organization=org)


class OrgScopedModel(UUIDModel, TimeStampedModel):
    """
    Anything that belongs to exactly one company. The organization link is
    required, so a developer cannot forget it.

    Always query through for_org:
        Environment.objects.for_org(request.organization)
    never Environment.objects.all() inside a company page.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )

    objects = OrgScopedQuerySet.as_manager()

    class Meta:
        abstract = True


class OrgScopedSoftDeleteQuerySet(OrgScopedQuerySet, SoftDeleteQuerySet):
    """for_org + active/deleted/restore/hard_delete in one queryset."""


class OrgScopedSoftDeleteManager(
    models.Manager.from_queryset(OrgScopedSoftDeleteQuerySet)
):
    """Default manager for tenant-owned, soft-deletable models."""

    def get_queryset(self):
        return super().get_queryset().active()


class OrgScopedSoftDeleteModel(OrgScopedModel, SoftDeleteMixin):
    """Tenant-owned AND soft-deletable. Use only where recovery is needed."""

    objects = OrgScopedSoftDeleteManager()
    all_objects = models.Manager.from_queryset(OrgScopedSoftDeleteQuerySet)()

    class Meta:
        abstract = True
