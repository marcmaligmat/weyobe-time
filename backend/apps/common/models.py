"""
Common models following SOLID principles.

This module provides base models that follow:
- Single Responsibility: Each model has one clear purpose
- Open/Closed: Extensible through inheritance
- Interface Segregation: Focused mixins for specific functionality
"""

import uuid
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model that provides timestamps.

    Follows Single Responsibility Principle - only handles timestamps.
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that provides UUID primary key.

    Follows Single Responsibility Principle - only handles UUID generation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.

    Follows Single Responsibility Principle - only handles soft deletion.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        """Soft delete the instance."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the instance."""
        super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True


class AuditModel(models.Model):
    """
    Abstract base model that provides audit trail functionality.

    Follows Single Responsibility Principle - only handles audit tracking.
    """
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_updated'
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Base model that combines common functionality.

    Follows Open/Closed Principle - can be extended without modification.
    """
    class Meta:
        abstract = True


class OrganizationScopedModel(BaseModel):
    """
    Abstract base model for multi-tenant organization-scoped models.

    Follows Single Responsibility Principle - only handles organization scoping.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
        ]


class StatusChoicesMixin:
    """
    Mixin that provides common status choices.

    Follows Interface Segregation Principle - focused on status management.
    """
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (SUSPENDED, 'Suspended'),
    ]


class ApprovalStatusMixin:
    """
    Mixin that provides approval status choices.

    Follows Interface Segregation Principle - focused on approval workflow.
    """
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    APPROVAL_STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SUBMITTED, 'Submitted'),
        (PENDING, 'Pending Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]