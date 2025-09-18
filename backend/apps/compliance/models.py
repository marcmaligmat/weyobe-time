"""
Compliance models following SOLID principles.

This module provides compliance monitoring models that follow:
- Single Responsibility: Each model handles one aspect of compliance
- Open/Closed: Extensible for different compliance rules
- Interface Segregation: Focused interfaces for different alerts
"""

from django.db import models
from apps.common.models import OrganizationScopedModel


class ComplianceAlert(OrganizationScopedModel):
    """
    Model for compliance alerts and violations.

    Follows Single Responsibility Principle - only manages compliance alerts.
    """
    ALERT_TYPE_CHOICES = [
        ('overtime', 'Overtime Violation'),
        ('missed_break', 'Missed Break'),
        ('long_shift', 'Long Shift'),
        ('consecutive_days', 'Consecutive Days'),
        ('late_submission', 'Late Time Submission'),
        ('missing_clockout', 'Missing Clock Out'),
    ]

    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='compliance_alerts'
    )
    time_entry = models.ForeignKey(
        'time_tracking.TimeEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='compliance_alerts'
    )

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    message = models.TextField()

    # Alert details
    threshold_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Status
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Compliance Alert'
        verbose_name_plural = 'Compliance Alerts'
        indexes = [
            models.Index(fields=['user', 'alert_type']),
            models.Index(fields=['severity', 'is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.user.get_full_name()}"