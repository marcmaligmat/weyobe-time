"""
Approval workflow models following SOLID principles.

This module provides approval workflow models that follow:
- Single Responsibility: Each model handles one aspect of approval workflows
- Open/Closed: Extensible for different approval types
"""

from django.db import models
from apps.common.models import OrganizationScopedModel, ApprovalStatusMixin


class ApprovalWorkflow(OrganizationScopedModel):
    """
    Model for defining approval workflows.

    Follows Single Responsibility Principle - only manages workflow definitions.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Workflow configuration
    approval_type = models.CharField(
        max_length=20,
        choices=[
            ('time_entry', 'Time Entry'),
            ('overtime', 'Overtime'),
            ('modification', 'Time Modification'),
            ('project', 'Project'),
        ]
    )

    # Approval hierarchy
    requires_manager_approval = models.BooleanField(default=True)
    requires_admin_approval = models.BooleanField(default=False)
    auto_approve_threshold = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Approval Workflow'
        verbose_name_plural = 'Approval Workflows'
        unique_together = ['organization', 'approval_type']

    def __str__(self):
        return f"{self.name} - {self.get_approval_type_display()}"