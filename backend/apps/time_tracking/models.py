"""
Time tracking models following SOLID principles.

This module provides time tracking models that follow:
- Single Responsibility: Each model handles one aspect of time tracking
- Open/Closed: Extensible for different time entry types
- Liskov Substitution: Time entry types can be substituted
- Interface Segregation: Focused interfaces for different concerns
- Dependency Inversion: Abstract time tracking interface
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.common.models import OrganizationScopedModel, ApprovalStatusMixin


class BreakEntry(OrganizationScopedModel):
    """
    Break entry model for tracking breaks within time entries.

    Follows Single Responsibility Principle - only manages break tracking.
    """
    BREAK_TYPE_CHOICES = [
        ('short_break', 'Short Break'),
        ('lunch', 'Lunch Break'),
        ('personal', 'Personal Break'),
        ('meeting', 'Meeting Break'),
        ('other', 'Other'),
    ]

    time_entry = models.ForeignKey(
        'TimeEntry',
        on_delete=models.CASCADE,
        related_name='break_entries'
    )
    break_type = models.CharField(max_length=20, choices=BREAK_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    # Duration in minutes (calculated or manual)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Whether this break is paid
    is_paid = models.BooleanField(default=False)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Break Entry'
        verbose_name_plural = 'Break Entries'
        indexes = [
            models.Index(fields=['time_entry', 'start_time']),
            models.Index(fields=['break_type']),
        ]

    def __str__(self):
        return f"{self.get_break_type_display()} - {self.start_time.strftime('%H:%M')}"

    def save(self, *args, **kwargs):
        """Calculate duration if end_time is provided."""
        if self.start_time and self.end_time and not self.duration_minutes:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if break is currently active (no end time)."""
        return self.end_time is None

    @property
    def duration_hours(self):
        """Get duration in hours."""
        if self.duration_minutes:
            return Decimal(self.duration_minutes) / 60
        return Decimal('0.00')


class TimeEntry(OrganizationScopedModel, ApprovalStatusMixin):
    """
    Main time entry model for tracking work time.

    Follows Single Responsibility Principle - manages time entry data.
    Follows Open/Closed Principle - can be extended for different entry types.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )
    task = models.ForeignKey(
        'projects.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )

    # Date and time
    date = models.DateField()
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)

    # Manual time entry fields
    is_manual_entry = models.BooleanField(default=False)
    manual_start_time = models.TimeField(null=True, blank=True)
    manual_end_time = models.TimeField(null=True, blank=True)

    # Time calculations
    regular_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    break_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Billing information
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    billable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Description and notes
    description = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatusMixin.APPROVAL_STATUS_CHOICES,
        default=ApprovalStatusMixin.DRAFT
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_time_entries'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)

    # Location tracking (optional)
    clock_in_location = models.JSONField(default=dict, blank=True)
    clock_out_location = models.JSONField(default=dict, blank=True)
    is_remote = models.BooleanField(default=False)

    # Flags
    is_locked = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Time Entry'
        verbose_name_plural = 'Time Entries'
        unique_together = ['user', 'date', 'clock_in']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['project', 'date']),
            models.Index(fields=['task', 'date']),
            models.Index(fields=['organization', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_billable']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date} ({self.total_hours}h)"

    def save(self, *args, **kwargs):
        """Calculate hours and amounts on save."""
        self.calculate_hours()
        self.calculate_billing()
        super().save(*args, **kwargs)

    def calculate_hours(self):
        """Calculate regular, overtime, and total hours."""
        if not self.clock_in:
            return

        # Calculate work duration
        if self.clock_out:
            work_duration = self.clock_out - self.clock_in
        else:
            work_duration = timezone.now() - self.clock_in

        # Convert to hours
        work_hours = Decimal(work_duration.total_seconds() / 3600)

        # Subtract break time
        break_duration = sum(
            break_entry.duration_hours
            for break_entry in self.break_entries.all()
            if not break_entry.is_paid
        )
        self.break_hours = break_duration

        net_work_hours = max(Decimal('0.00'), work_hours - break_duration)

        # Calculate regular and overtime
        if self.user and self.user.compliance_settings:
            daily_limit = self.user.compliance_settings.max_hours_per_day
        else:
            daily_limit = 8

        self.regular_hours = min(net_work_hours, Decimal(daily_limit))
        self.overtime_hours = max(Decimal('0.00'), net_work_hours - Decimal(daily_limit))
        self.total_hours = net_work_hours

    def calculate_billing(self):
        """Calculate billable amount."""
        if not self.is_billable or not self.hourly_rate:
            self.billable_amount = Decimal('0.00')
            return

        regular_amount = self.regular_hours * self.hourly_rate

        # Apply overtime multiplier
        if self.user and self.user.compliance_settings:
            overtime_multiplier = self.user.compliance_settings.overtime_rate_multiplier
        else:
            overtime_multiplier = Decimal('1.5')

        overtime_amount = self.overtime_hours * self.hourly_rate * overtime_multiplier

        self.billable_amount = regular_amount + overtime_amount

    @property
    def is_active(self):
        """Check if time entry is currently active (clocked in but not out)."""
        return self.clock_in and not self.clock_out

    @property
    def is_overtime(self):
        """Check if entry contains overtime hours."""
        return self.overtime_hours > 0

    @property
    def duration(self):
        """Get total duration including breaks."""
        if self.clock_in and self.clock_out:
            return self.clock_out - self.clock_in
        elif self.clock_in:
            return timezone.now() - self.clock_in
        return None

    def can_be_edited_by(self, user):
        """Check if user can edit this time entry."""
        # Own entries can be edited if not locked or approved
        if self.user == user and not self.is_locked and self.status not in ['approved']:
            return True

        # Managers can edit team entries
        if user.can_manage_user(self.user):
            return True

        return False

    def submit_for_approval(self):
        """Submit time entry for approval."""
        if self.status == self.DRAFT:
            self.status = self.SUBMITTED
            self.submitted_at = timezone.now()
            self.save(update_fields=['status', 'submitted_at'])

    def approve(self, approved_by, notes=''):
        """Approve time entry."""
        self.status = self.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.is_locked = True
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'approval_notes', 'is_locked'])

    def reject(self, rejected_by, notes=''):
        """Reject time entry."""
        self.status = self.REJECTED
        self.approved_by = rejected_by
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'approval_notes'])


class TimeModificationRequest(OrganizationScopedModel, ApprovalStatusMixin):
    """
    Model for requesting modifications to time entries.

    Follows Single Responsibility Principle - only handles modification requests.
    """
    time_entry = models.ForeignKey(
        TimeEntry,
        on_delete=models.CASCADE,
        related_name='modification_requests'
    )
    requested_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='time_modification_requests'
    )

    # Requested changes (JSON field with original and new values)
    requested_changes = models.JSONField()
    reason = models.TextField()

    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatusMixin.APPROVAL_STATUS_CHOICES,
        default=ApprovalStatusMixin.PENDING
    )
    reviewed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_modification_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Time Modification Request'
        verbose_name_plural = 'Time Modification Requests'
        indexes = [
            models.Index(fields=['time_entry']),
            models.Index(fields=['requested_by']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Modification request for {self.time_entry}"

    def approve(self, reviewer, notes=''):
        """Approve modification request and apply changes."""
        self.status = self.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()

        # Apply changes to time entry
        for field, new_value in self.requested_changes.items():
            if hasattr(self.time_entry, field):
                setattr(self.time_entry, field, new_value)

        self.time_entry.save()

    def reject(self, reviewer, notes=''):
        """Reject modification request."""
        self.status = self.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()


class TimesheetPeriod(OrganizationScopedModel):
    """
    Model for managing timesheet periods and payroll cycles.

    Follows Single Responsibility Principle - only manages timesheet periods.
    """
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    # Status
    is_open = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    # Approval deadlines
    submission_deadline = models.DateTimeField(null=True, blank=True)
    approval_deadline = models.DateTimeField(null=True, blank=True)

    # Payroll information
    payroll_processed = models.BooleanField(default=False)
    payroll_processed_at = models.DateTimeField(null=True, blank=True)
    payroll_processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_timesheet_periods'
    )

    class Meta:
        verbose_name = 'Timesheet Period'
        verbose_name_plural = 'Timesheet Periods'
        unique_together = ['organization', 'start_date', 'end_date']
        indexes = [
            models.Index(fields=['organization', 'start_date', 'end_date']),
            models.Index(fields=['is_open', 'is_locked']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def get_time_entries(self):
        """Get all time entries for this period."""
        return TimeEntry.objects.filter(
            organization=self.organization,
            date__gte=self.start_date,
            date__lte=self.end_date,
            is_deleted=False
        )

    def get_total_hours(self):
        """Get total hours for this period."""
        return self.get_time_entries().aggregate(
            total=models.Sum('total_hours')
        )['total'] or Decimal('0.00')

    def get_total_billable_amount(self):
        """Get total billable amount for this period."""
        return self.get_time_entries().filter(
            is_billable=True
        ).aggregate(
            total=models.Sum('billable_amount')
        )['total'] or Decimal('0.00')

    def close_period(self):
        """Close the timesheet period."""
        self.is_open = False
        self.save(update_fields=['is_open'])

    def lock_period(self):
        """Lock the timesheet period (prevent further changes)."""
        self.is_locked = True
        self.save(update_fields=['is_locked'])

        # Lock all time entries in this period
        self.get_time_entries().update(is_locked=True)