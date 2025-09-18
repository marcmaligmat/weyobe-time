"""
User models following SOLID principles.

This module provides user-related models that follow:
- Single Responsibility: Each model handles one aspect of user management
- Open/Closed: Extensible for different user types and roles
- Liskov Substitution: Role permissions can be substituted
- Interface Segregation: Focused interfaces for different user concerns
- Dependency Inversion: Abstract user interface
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from apps.common.models import BaseModel, TimestampedModel


class Role(BaseModel):
    """
    Role model for role-based access control.

    Follows Single Responsibility Principle - only manages roles.
    """
    EMPLOYEE = 'employee'
    CONTRACTOR = 'contractor'
    TEAM_LEAD = 'team_lead'
    MANAGER = 'manager'
    ADMIN = 'admin'
    CLIENT_ADMIN = 'client_admin'
    GLOBAL_ADMIN = 'global_admin'

    ROLE_CHOICES = [
        (EMPLOYEE, 'Employee'),
        (CONTRACTOR, 'Contractor'),
        (TEAM_LEAD, 'Team Lead'),
        (MANAGER, 'Manager'),
        (ADMIN, 'Admin'),
        (CLIENT_ADMIN, 'Client Admin'),
        (GLOBAL_ADMIN, 'Global Admin'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_roles'
    )

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.get_name_display()


class UserProfile(BaseModel):
    """
    User profile model for additional user information.

    Follows Single Responsibility Principle - only handles profile data.
    """
    # Personal information
    phone = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)

    # Avatar
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Preferences
    timezone = models.CharField(max_length=50, default='America/New_York')
    date_format = models.CharField(max_length=20, default='MM/dd/yyyy')
    time_format = models.CharField(max_length=10, default='12')  # 12 or 24 hour
    language = models.CharField(max_length=10, default='en')

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    desktop_notifications = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile for {self.user.get_full_name() if hasattr(self, 'user') else 'Unknown'}"


class ComplianceSettings(BaseModel):
    """
    User-specific compliance settings.

    Follows Single Responsibility Principle - only handles compliance configuration.
    """
    # Hour limits
    max_hours_per_day = models.PositiveIntegerField(default=8)
    max_hours_per_week = models.PositiveIntegerField(default=40)
    max_consecutive_days = models.PositiveIntegerField(default=6)

    # Break requirements
    require_breaks = models.BooleanField(default=True)
    break_after_hours = models.PositiveIntegerField(default=4)
    break_duration_minutes = models.PositiveIntegerField(default=15)

    # Lunch requirements
    require_lunch = models.BooleanField(default=True)
    lunch_after_hours = models.PositiveIntegerField(default=6)
    lunch_duration_minutes = models.PositiveIntegerField(default=60)

    # Overtime settings
    overtime_rate_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.5)
    night_shift_differential = models.DecimalField(max_digits=4, decimal_places=2, default=0.1)
    weekend_rate_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)

    # Approval requirements
    require_approval_for_overtime = models.BooleanField(default=True)
    require_approval_for_time_edits = models.BooleanField(default=True)
    auto_approve_regular_hours = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Compliance Settings'
        verbose_name_plural = 'Compliance Settings'

    def __str__(self):
        return f"Compliance settings for {self.user.get_full_name() if hasattr(self, 'user') else 'Unknown'}"


class User(AbstractUser):
    """
    Custom user model with organization support.

    Follows Single Responsibility Principle - manages user authentication and basic info.
    Follows Open/Closed Principle - can be extended with additional profile models.
    """
    # Override the username field to use email
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Organization relationships
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    # Role and permissions
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    # Employment information
    employee_id = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Employee ID can only contain uppercase letters, numbers, and hyphens.'
            )
        ]
    )
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    # Compensation
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')

    # Manager relationship
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )

    # Profile relationships (one-to-one)
    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='user',
        null=True,
        blank=True
    )
    compliance_settings = models.OneToOneField(
        ComplianceSettings,
        on_delete=models.CASCADE,
        related_name='user',
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['department']),
            models.Index(fields=['manager']),
        ]

    def __str__(self):
        return self.get_full_name() or self.email

    def save(self, *args, **kwargs):
        """Override save to create related profile objects."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Create default profile and compliance settings for new users
        if is_new:
            if not self.profile:
                profile = UserProfile.objects.create()
                self.profile = profile
                self.save(update_fields=['profile'])

            if not self.compliance_settings:
                compliance_settings = ComplianceSettings.objects.create()
                self.compliance_settings = compliance_settings
                self.save(update_fields=['compliance_settings'])

    @property
    def role_name(self):
        """Get role name display."""
        return self.role.get_name_display() if self.role else 'No Role'

    @property
    def department_name(self):
        """Get department name."""
        return self.department.name if self.department else 'No Department'

    @property
    def organization_name(self):
        """Get organization name."""
        return self.organization.name if self.organization else 'No Organization'

    def has_role(self, role_name):
        """Check if user has specific role."""
        return self.role and self.role.name == role_name

    def has_any_role(self, role_names):
        """Check if user has any of the specified roles."""
        return self.role and self.role.name in role_names

    def can_manage_user(self, other_user):
        """Check if user can manage another user."""
        if not self.role:
            return False

        # Global admin can manage all users
        if self.role.name == Role.GLOBAL_ADMIN:
            return True

        # Admin can manage users in same organization
        if self.role.name == Role.ADMIN and self.organization == other_user.organization:
            return True

        # Manager can manage direct reports
        if self.role.name in [Role.MANAGER, Role.TEAM_LEAD]:
            return other_user.manager == self or other_user in self.get_all_reports()

        return False

    def get_all_reports(self):
        """Get all direct and indirect reports."""
        reports = []
        for direct_report in self.direct_reports.filter(is_active=True, is_deleted=False):
            reports.append(direct_report)
            reports.extend(direct_report.get_all_reports())
        return reports

    def get_accessible_organizations(self):
        """Get all organizations user has access to."""
        if self.role and self.role.name == Role.GLOBAL_ADMIN:
            from apps.organizations.models import Organization
            return Organization.objects.filter(is_active=True, is_deleted=False)
        elif self.organization:
            return [self.organization]
        return []

    def get_manageable_departments(self):
        """Get all departments user can manage."""
        if not self.organization:
            return []

        if self.role and self.role.name in [Role.ADMIN, Role.GLOBAL_ADMIN]:
            return self.organization.get_departments()
        elif self.role and self.role.name in [Role.MANAGER, Role.TEAM_LEAD]:
            return [self.department] if self.department else []
        return []


class UserSession(TimestampedModel):
    """
    User session tracking for security and audit purposes.

    Follows Single Responsibility Principle - only handles session tracking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"