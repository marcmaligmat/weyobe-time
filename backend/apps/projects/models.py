"""
Project models following SOLID principles.

This module provides project-related models that follow:
- Single Responsibility: Each model handles one aspect of project management
- Open/Closed: Extensible for different project types
- Liskov Substitution: Project types can be substituted
- Interface Segregation: Focused interfaces for different concerns
- Dependency Inversion: Abstract project interface
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import OrganizationScopedModel, StatusChoicesMixin


class Client(OrganizationScopedModel, StatusChoicesMixin):
    """
    Client model for project management.

    Follows Single Responsibility Principle - only manages client information.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Address information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Business information
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=20,
        choices=[
            ('startup', 'Startup (1-10)'),
            ('small', 'Small (11-50)'),
            ('medium', 'Medium (51-200)'),
            ('large', 'Large (201-1000)'),
            ('enterprise', 'Enterprise (1000+)'),
        ],
        blank=True
    )

    # Billing information
    billing_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    payment_terms = models.CharField(max_length=50, default='Net 30')

    # Relationship management
    primary_contact = models.CharField(max_length=255, blank=True)
    account_manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_clients'
    )

    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoicesMixin.STATUS_CHOICES,
        default=StatusChoicesMixin.ACTIVE
    )

    # Notes and documentation
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['account_manager']),
        ]

    def __str__(self):
        return self.name

    @property
    def active_projects_count(self):
        """Get count of active projects for this client."""
        return self.projects.filter(
            status__in=['active', 'in_progress'],
            is_deleted=False
        ).count()

    def get_total_revenue(self):
        """Calculate total revenue from this client."""
        # This would be calculated from time entries and billing
        return 0  # Placeholder


class ProjectCategory(OrganizationScopedModel):
    """
    Project category model for organization.

    Follows Single Responsibility Principle - only manages project categorization.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'
        unique_together = ['organization', 'name']

    def __str__(self):
        return self.name


class Project(OrganizationScopedModel, StatusChoicesMixin):
    """
    Main project model.

    Follows Single Responsibility Principle - manages project information.
    Follows Open/Closed Principle - can be extended for specialized project types.
    """
    PROJECT_STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=20, blank=True)

    # Relationships
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )

    # Project management
    project_manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(
        'users.User',
        through='ProjectMembership',
        related_name='assigned_projects'
    )

    # Timeline
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    # Budget and billing
    budget_hours = models.PositiveIntegerField(null=True, blank=True)
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_billable = models.BooleanField(default=True)
    billing_type = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('fixed', 'Fixed Price'),
            ('retainer', 'Retainer'),
            ('non_billable', 'Non-Billable'),
        ],
        default='hourly'
    )

    # Status and priority
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='planning'
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )

    # Progress tracking
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Settings
    allow_time_tracking = models.BooleanField(default=True)
    require_description = models.BooleanField(default=False)
    auto_calculate_progress = models.BooleanField(default=True)

    # Active status
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'status', 'is_active']),
            models.Index(fields=['client']),
            models.Index(fields=['department']),
            models.Index(fields=['project_manager']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_overdue(self):
        """Check if project is overdue."""
        if self.deadline and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now().date() > self.deadline
        return False

    @property
    def total_hours_logged(self):
        """Get total hours logged on this project."""
        from apps.time_tracking.models import TimeEntry
        return TimeEntry.objects.filter(
            project=self,
            is_deleted=False
        ).aggregate(
            total=models.Sum('total_hours')
        )['total'] or 0

    @property
    def remaining_hours(self):
        """Get remaining hours in budget."""
        if self.budget_hours:
            return max(0, self.budget_hours - self.total_hours_logged)
        return None

    @property
    def budget_utilization(self):
        """Get budget utilization percentage."""
        if self.budget_hours and self.budget_hours > 0:
            return min(100, (self.total_hours_logged / self.budget_hours) * 100)
        return 0

    def get_team_members(self):
        """Get all active team members."""
        return self.team_members.filter(
            is_active=True,
            is_deleted=False,
            projectmembership__is_active=True
        )

    def can_user_log_time(self, user):
        """Check if user can log time to this project."""
        if not self.allow_time_tracking or not self.is_active:
            return False

        # Project manager can always log time
        if self.project_manager == user:
            return True

        # Team members can log time
        return self.team_members.filter(id=user.id).exists()


class ProjectMembership(OrganizationScopedModel):
    """
    Project membership model for team assignments.

    Follows Single Responsibility Principle - only manages project-user relationships.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    # Role in project
    role = models.CharField(
        max_length=50,
        choices=[
            ('member', 'Team Member'),
            ('lead', 'Team Lead'),
            ('developer', 'Developer'),
            ('designer', 'Designer'),
            ('qa', 'QA Engineer'),
            ('analyst', 'Business Analyst'),
            ('consultant', 'Consultant'),
        ],
        default='member'
    )

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # Allocation
    allocation_percentage = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Permissions
    can_view_budget = models.BooleanField(default=False)
    can_edit_project = models.BooleanField(default=False)
    can_manage_team = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Project Membership'
        verbose_name_plural = 'Project Memberships'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name}"

    @property
    def is_current(self):
        """Check if membership is currently active."""
        if not self.is_active:
            return False

        from django.utils import timezone
        today = timezone.now().date()

        if self.start_date > today:
            return False

        if self.end_date and self.end_date < today:
            return False

        return True