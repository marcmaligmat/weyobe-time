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
from django.utils import timezone
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


class OrganizationMember(BaseModel):
    """
    Organization membership model with role-based permissions.

    Follows Single Responsibility Principle - only manages organization membership.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )

    # Role and permissions
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    # Dates
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Permissions
    can_invite_users = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_teams = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_manage_settings = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)

    # Invitation details
    invited_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_memberships'
    )

    class Meta:
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name}"

    def save(self, *args, **kwargs):
        """Set default permissions based on role."""
        if self.pk is None:  # New instance
            self.set_default_permissions()
        super().save(*args, **kwargs)

    def set_default_permissions(self):
        """Set default permissions based on role."""
        if self.role == 'admin':
            self.can_invite_users = True
            self.can_manage_projects = True
            self.can_manage_teams = True
            self.can_view_reports = True
            self.can_manage_settings = True
            self.can_manage_billing = True
        elif self.role == 'manager':
            self.can_invite_users = True
            self.can_manage_projects = True
            self.can_manage_teams = True
            self.can_view_reports = True
            self.can_manage_settings = False
            self.can_manage_billing = False
        else:  # member
            self.can_invite_users = False
            self.can_manage_projects = False
            self.can_manage_teams = False
            self.can_view_reports = True
            self.can_manage_settings = False
            self.can_manage_billing = False

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'

    @property
    def is_manager(self):
        """Check if user is a manager."""
        return self.role == 'manager'

    @property
    def is_member(self):
        """Check if user is a member."""
        return self.role == 'member'

    def has_permission(self, permission):
        """Check if user has specific permission."""
        return getattr(self, f'can_{permission}', False)

    def promote_to_manager(self):
        """Promote member to manager."""
        if self.role == 'member':
            self.role = 'manager'
            self.set_default_permissions()
            self.save()

    def promote_to_admin(self):
        """Promote member/manager to admin."""
        if self.role in ['member', 'manager']:
            self.role = 'admin'
            self.set_default_permissions()
            self.save()

    def demote_to_member(self):
        """Demote manager/admin to member."""
        if self.role in ['manager', 'admin']:
            self.role = 'member'
            self.set_default_permissions()
            self.save()


class Invitation(BaseModel):
    """
    Invitation model for inviting users to organizations.

    Follows Single Responsibility Principle - only manages invitations.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField()

    # Inviter information
    invited_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )

    # Role and department for the invited user
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.ROLE_CHOICES,
        default='member'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations'
    )

    # Invitation details
    message = models.TextField(blank=True)
    token = models.CharField(max_length=255, unique=True)

    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invitations'
    )

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
        unique_together = ['organization', 'email', 'status']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"

    def save(self, *args, **kwargs):
        """Generate token and set expiration if new."""
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)

        if not self.expires_at:
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(days=7)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if invitation is expired."""
        return timezone.now() > self.expires_at

    @property
    def is_pending(self):
        """Check if invitation is pending."""
        return self.status == 'pending' and not self.is_expired

    def accept(self, user):
        """Accept the invitation."""
        if not self.is_pending:
            raise ValueError("Invitation is not in pending status or has expired")

        if user.email != self.email:
            raise ValueError("User email does not match invitation email")

        # Create organization membership
        membership, created = OrganizationMember.objects.get_or_create(
            organization=self.organization,
            user=user,
            defaults={
                'role': self.role,
                'invited_by': self.invited_by,
            }
        )

        # Update user's organization if not set
        if not user.organization:
            user.organization = self.organization
            if self.department:
                user.department = self.department
            user.save(update_fields=['organization', 'department'])

        # Update invitation status
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save(update_fields=['status', 'accepted_at', 'accepted_by'])

        return membership

    def decline(self):
        """Decline the invitation."""
        if not self.is_pending:
            raise ValueError("Invitation is not in pending status")

        self.status = 'declined'
        self.save(update_fields=['status'])

    def cancel(self):
        """Cancel the invitation."""
        if self.status not in ['pending']:
            raise ValueError("Can only cancel pending invitations")

        self.status = 'cancelled'
        self.save(update_fields=['status'])

    def extend_expiration(self, days=7):
        """Extend invitation expiration."""
        if self.status != 'pending':
            raise ValueError("Can only extend pending invitations")

        from datetime import timedelta
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=['expires_at'])

    @classmethod
    def cleanup_expired(cls):
        """Mark expired invitations as expired."""
        expired_invitations = cls.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        expired_invitations.update(status='expired')