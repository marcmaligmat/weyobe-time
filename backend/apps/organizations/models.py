"""
Organization models following SOLID principles.

This module provides organization-related models that follow:
- Single Responsibility: Each model handles one aspect of organization management
- Open/Closed: Extensible for different organization types
- Liskov Substitution: Organization settings can be substituted
- Interface Segregation: Focused interfaces for different concerns
- Dependency Inversion: Abstract settings interface
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify
from apps.common.models import BaseModel, StatusChoicesMixin


class OrganizationSettings(BaseModel):
    """
    Organization-specific settings model.

    Follows Single Responsibility Principle - only handles organization settings.
    """
    # Work schedule settings
    work_hours_per_day = models.PositiveIntegerField(default=8)
    work_days_per_week = models.PositiveIntegerField(default=5)
    overtime_threshold_daily = models.PositiveIntegerField(default=8)
    overtime_threshold_weekly = models.PositiveIntegerField(default=40)

    # Break and lunch settings
    break_duration_minutes = models.PositiveIntegerField(default=15)
    lunch_duration_minutes = models.PositiveIntegerField(default=60)
    break_after_hours = models.PositiveIntegerField(default=4)
    lunch_after_hours = models.PositiveIntegerField(default=6)

    # Time tracking settings
    allow_manual_time_entry = models.BooleanField(default=True)
    require_project_time_allocation = models.BooleanField(default=True)
    allow_future_time_entries = models.BooleanField(default=False)
    max_daily_hours = models.PositiveIntegerField(default=12)

    # Approval settings
    require_time_approval = models.BooleanField(default=True)
    auto_approve_regular_hours = models.BooleanField(default=False)
    require_overtime_approval = models.BooleanField(default=True)

    # Compliance settings
    enable_compliance_monitoring = models.BooleanField(default=True)
    overtime_rate_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.5)
    night_shift_differential = models.DecimalField(max_digits=4, decimal_places=2, default=0.1)

    # Notification settings
    send_overtime_alerts = models.BooleanField(default=True)
    send_break_reminders = models.BooleanField(default=True)
    alert_manager_on_violations = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Organization Settings'
        verbose_name_plural = 'Organization Settings'

    def __str__(self):
        return f"Settings for {self.organization.name if hasattr(self, 'organization') else 'Unknown'}"


class Organization(BaseModel, StatusChoicesMixin):
    """
    Main organization model for multi-tenant architecture.

    Follows Single Responsibility Principle - manages organization data.
    Follows Open/Closed Principle - can be extended for specialized organization types.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9-]+$',
                message='Slug can only contain lowercase letters, numbers, and hyphens.'
            )
        ]
    )
    description = models.TextField(blank=True)

    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Address information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')

    # Settings
    timezone = models.CharField(max_length=50, default='America/New_York')
    currency = models.CharField(max_length=3, default='USD')
    date_format = models.CharField(max_length=20, default='MM/dd/yyyy')
    time_format = models.CharField(max_length=10, default='12')  # 12 or 24 hour

    # Status and control
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoicesMixin.STATUS_CHOICES,
        default=StatusChoicesMixin.ACTIVE
    )

    # Subscription information
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ('free', 'Free'),
            ('basic', 'Basic'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    max_users = models.PositiveIntegerField(default=10)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)

    # Organization settings (one-to-one relationship)
    settings = models.OneToOneField(
        OrganizationSettings,
        on_delete=models.CASCADE,
        related_name='organization',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'status']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug and create settings."""
        if not self.slug:
            self.slug = slugify(self.name)

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Create default settings for new organizations
        if is_new and not self.settings:
            settings = OrganizationSettings.objects.create()
            self.settings = settings
            self.save(update_fields=['settings'])

    @property
    def user_count(self):
        """Get current number of users in organization."""
        return self.users.filter(is_active=True).count()

    @property
    def is_subscription_active(self):
        """Check if organization subscription is active."""
        if self.subscription_expires_at:
            from django.utils import timezone
            return timezone.now() < self.subscription_expires_at
        return True

    def can_add_user(self):
        """Check if organization can add more users."""
        return self.user_count < self.max_users

    def get_active_users(self):
        """Get all active users in organization."""
        return self.users.filter(is_active=True, is_deleted=False)

    def get_departments(self):
        """Get all departments in organization."""
        return self.departments.filter(is_deleted=False)

    def get_projects(self):
        """Get all projects in organization."""
        return self.projects.filter(is_deleted=False)


class Department(BaseModel, StatusChoicesMixin):
    """
    Department model for organizational hierarchy.

    Follows Single Responsibility Principle - manages department structure.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=20, blank=True)

    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subdepartments'
    )

    # Department lead
    manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )

    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoicesMixin.STATUS_CHOICES,
        default=StatusChoicesMixin.ACTIVE
    )

    # Budget and cost center
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_center = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    @property
    def full_name(self):
        """Get full hierarchical name of department."""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    def get_all_children(self):
        """Get all descendant departments."""
        children = []
        for child in self.subdepartments.filter(is_deleted=False):
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_all_users(self):
        """Get all users in this department and subdepartments."""
        department_ids = [self.id] + [child.id for child in self.get_all_children()]
        return self.organization.users.filter(
            department_id__in=department_ids,
            is_active=True,
            is_deleted=False
        )

    def get_projects(self):
        """Get all projects in this department."""
        return self.projects.filter(is_deleted=False)