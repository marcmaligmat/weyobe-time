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
from django.utils import timezone
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
    teams = models.ManyToManyField(
        'Team',
        blank=True,
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


class Team(OrganizationScopedModel, StatusChoicesMixin):
    """
    Team model for grouping users within organizations.

    Follows Single Responsibility Principle - only manages team structure.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=20, blank=True)

    # Team lead
    team_lead = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )

    # Department relationship
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams'
    )

    # Team members (many-to-many through TeamMember)
    members = models.ManyToManyField(
        'users.User',
        through='TeamMember',
        related_name='teams'
    )

    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoicesMixin.STATUS_CHOICES,
        default=StatusChoicesMixin.ACTIVE
    )

    # Team settings
    max_members = models.PositiveIntegerField(default=50)
    is_public = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['department']),
            models.Index(fields=['team_lead']),
        ]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Get current number of active members."""
        return self.members.filter(
            teammember__is_active=True,
            is_active=True,
            is_deleted=False
        ).count()

    def can_add_member(self):
        """Check if team can add more members."""
        return self.member_count < self.max_members

    def get_active_members(self):
        """Get all active team members."""
        return self.members.filter(
            teammember__is_active=True,
            is_active=True,
            is_deleted=False
        )

    def get_projects(self):
        """Get all projects assigned to this team."""
        return self.assigned_projects.filter(is_deleted=False)

    def add_member(self, user, role='member', allocation_percentage=100):
        """Add a user to the team."""
        if not self.can_add_member():
            raise ValueError("Team has reached maximum capacity")

        team_member, created = TeamMember.objects.get_or_create(
            team=self,
            user=user,
            defaults={
                'organization': self.organization,
                'role': role,
                'allocation_percentage': allocation_percentage,
            }
        )
        return team_member

    def remove_member(self, user):
        """Remove a user from the team."""
        try:
            team_member = TeamMember.objects.get(team=self, user=user)
            team_member.is_active = False
            team_member.end_date = timezone.now().date()
            team_member.save()
        except TeamMember.DoesNotExist:
            pass


class TeamMember(OrganizationScopedModel):
    """
    Team membership model for user-team relationships.

    Follows Single Responsibility Principle - only manages team membership.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='team_memberships')

    # Role in team
    role = models.CharField(
        max_length=50,
        choices=[
            ('member', 'Team Member'),
            ('lead', 'Team Lead'),
            ('senior', 'Senior Member'),
            ('junior', 'Junior Member'),
            ('intern', 'Intern'),
            ('contractor', 'Contractor'),
            ('consultant', 'Consultant'),
        ],
        default='member'
    )

    # Dates
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    # Allocation
    allocation_percentage = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Permissions within team
    can_view_all_projects = models.BooleanField(default=True)
    can_create_projects = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        unique_together = ['team', 'user']
        indexes = [
            models.Index(fields=['team', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"

    @property
    def is_current(self):
        """Check if membership is currently active."""
        if not self.is_active:
            return False

        today = timezone.now().date()

        if self.start_date > today:
            return False

        if self.end_date and self.end_date < today:
            return False

        return True

    @property
    def is_team_lead(self):
        """Check if user is the team lead."""
        return self.team.team_lead == self.user

    def can_manage_team(self):
        """Check if user can manage team settings."""
        return self.is_team_lead or self.can_manage_members


class Task(OrganizationScopedModel, StatusChoicesMixin):
    """
    Task model for project task management.

    Follows Single Responsibility Principle - only manages task data.
    """
    TASK_STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('testing', 'Testing'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )

    # Assignment
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )

    # Timeline
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)

    # Estimates and tracking
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Status and priority
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Progress
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Task settings
    is_billable = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    is_milestone = models.BooleanField(default=False)

    # Active status
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['project', 'status', 'is_active']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['parent_task']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status not in ['done', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False

    @property
    def is_completed(self):
        """Check if task is completed."""
        return self.status == 'done'

    @property
    def hours_variance(self):
        """Calculate variance between estimated and actual hours."""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None

    @property
    def completion_percentage(self):
        """Get task completion percentage based on status."""
        status_progress_map = {
            'todo': 0,
            'in_progress': 25,
            'review': 75,
            'testing': 90,
            'done': 100,
            'cancelled': 0,
        }
        return status_progress_map.get(self.status, 0)

    def get_subtasks(self):
        """Get all active subtasks."""
        return self.subtasks.filter(is_active=True, is_deleted=False)

    def get_time_entries(self):
        """Get all time entries for this task."""
        from apps.time_tracking.models import TimeEntry
        return TimeEntry.objects.filter(
            task=self,
            is_deleted=False
        )

    def update_actual_hours(self):
        """Update actual hours from time entries."""
        total_hours = self.get_time_entries().aggregate(
            total=models.Sum('total_hours')
        )['total'] or Decimal('0.00')

        self.actual_hours = total_hours
        self.save(update_fields=['actual_hours'])

    def assign_to(self, user):
        """Assign task to a user."""
        if not self.project.can_user_log_time(user):
            raise ValueError("User cannot be assigned to this task")

        self.assigned_to = user
        self.save(update_fields=['assigned_to'])

    def mark_completed(self, completed_by=None):
        """Mark task as completed."""
        self.status = 'done'
        self.completed_date = timezone.now().date()
        self.progress_percentage = 100

        if completed_by:
            # Log who completed the task in audit trail
            pass

        self.save(update_fields=['status', 'completed_date', 'progress_percentage'])

    def can_be_edited_by(self, user):
        """Check if user can edit this task."""
        # Task assignee can edit
        if self.assigned_to == user:
            return True

        # Task creator can edit
        if self.created_by == user:
            return True

        # Project manager can edit
        if self.project.project_manager == user:
            return True

        # User with manage permissions can edit
        if user.can_manage_user(self.assigned_to):
            return True

        return False