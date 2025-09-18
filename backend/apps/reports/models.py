"""
Reports models following SOLID principles.

This module provides reporting models that follow:
- Single Responsibility: Each model handles one aspect of reporting
- Open/Closed: Extensible for different report types
"""

from django.db import models
from apps.common.models import OrganizationScopedModel


class Report(OrganizationScopedModel):
    """
    Model for saved reports and report templates.

    Follows Single Responsibility Principle - only manages report definitions.
    """
    REPORT_TYPE_CHOICES = [
        ('timesheet', 'Timesheet Report'),
        ('project_summary', 'Project Summary'),
        ('user_productivity', 'User Productivity'),
        ('billing', 'Billing Report'),
        ('compliance', 'Compliance Report'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)

    # Report configuration
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    sort_order = models.JSONField(default=list)

    # Sharing and access
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        'users.User',
        blank=True,
        related_name='shared_reports'
    )

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        blank=True
    )
    next_run = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        indexes = [
            models.Index(fields=['organization', 'report_type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return self.name