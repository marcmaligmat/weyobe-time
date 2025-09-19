"""
Custom permission classes following SOLID principles.

This module provides permission classes that follow:
- Single Responsibility: Each permission handles one specific access rule
- Open/Closed: Extensible through inheritance
- Interface Segregation: Focused permissions for different use cases
- Dependency Inversion: Abstract permission interfaces
"""

from rest_framework import permissions
from apps.organizations.models import OrganizationMember


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.

    Follows Single Responsibility Principle - only handles organization membership.
    """

    def has_permission(self, request, view):
        """Check if user has organization membership."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        # Check if user is member of organization
        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True
        ).exists()


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the organization.

    Follows Single Responsibility Principle - only handles admin access.
    """

    def has_permission(self, request, view):
        """Check if user is organization admin."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.is_admin
        except OrganizationMember.DoesNotExist:
            return False


class IsOrganizationManagerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a manager or admin of the organization.

    Follows Single Responsibility Principle - only handles manager/admin access.
    """

    def has_permission(self, request, view):
        """Check if user is organization manager or admin."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.role in ['admin', 'manager']
        except OrganizationMember.DoesNotExist:
            return False


class HasOrganizationPermission(permissions.BasePermission):
    """
    Permission to check if user has specific organization permission.

    Usage: Add permission_required attribute to view.
    """

    def has_permission(self, request, view):
        """Check if user has required organization permission."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        permission_required = getattr(view, 'permission_required', None)
        if not permission_required:
            return True  # No specific permission required

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.has_permission(permission_required)
        except OrganizationMember.DoesNotExist:
            return False


class IsOwnerOrManager(permissions.BasePermission):
    """
    Permission to check if user is the owner of the object or has management rights.

    Follows Single Responsibility Principle - only handles ownership/management.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or can manage it."""
        if not request.user.is_authenticated:
            return False

        # Check if user owns the object
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Check if user can manage the object's owner
        if hasattr(obj, 'user') and hasattr(request.user, 'can_manage_user'):
            return request.user.can_manage_user(obj.user)

        return False


class IsProjectMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the project.

    Follows Single Responsibility Principle - only handles project membership.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is project member."""
        if not request.user.is_authenticated:
            return False

        # Get project from object
        project = getattr(obj, 'project', obj)

        # Check if user can log time to project
        return project.can_user_log_time(request.user)


class IsTeamMemberOrLead(permissions.BasePermission):
    """
    Permission to check if user is a member or lead of the team.

    Follows Single Responsibility Principle - only handles team membership.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is team member or lead."""
        if not request.user.is_authenticated:
            return False

        # Get team from object
        team = getattr(obj, 'team', obj)

        # Check if user is team lead
        if team.team_lead == request.user:
            return True

        # Check if user is team member
        return team.members.filter(
            id=request.user.id,
            teammember__is_active=True
        ).exists()


class CanInviteUsers(permissions.BasePermission):
    """
    Permission to check if user can invite other users to the organization.

    Follows Single Responsibility Principle - only handles invitation rights.
    """

    def has_permission(self, request, view):
        """Check if user can invite users."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.can_invite_users
        except OrganizationMember.DoesNotExist:
            return False


class CanManageProjects(permissions.BasePermission):
    """
    Permission to check if user can manage projects in the organization.

    Follows Single Responsibility Principle - only handles project management rights.
    """

    def has_permission(self, request, view):
        """Check if user can manage projects."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.can_manage_projects
        except OrganizationMember.DoesNotExist:
            return False


class CanManageTeams(permissions.BasePermission):
    """
    Permission to check if user can manage teams in the organization.

    Follows Single Responsibility Principle - only handles team management rights.
    """

    def has_permission(self, request, view):
        """Check if user can manage teams."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.can_manage_teams
        except OrganizationMember.DoesNotExist:
            return False


class CanViewReports(permissions.BasePermission):
    """
    Permission to check if user can view reports in the organization.

    Follows Single Responsibility Principle - only handles report viewing rights.
    """

    def has_permission(self, request, view):
        """Check if user can view reports."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.can_view_reports
        except OrganizationMember.DoesNotExist:
            return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read access to anyone, but write access only to the owner.

    Follows Open/Closed Principle - can be extended for specific ownership models.
    """

    def has_object_permission(self, request, view, obj):
        """Check ownership for write operations."""
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner
        return hasattr(obj, 'user') and obj.user == request.user


class OrganizationScopedPermission(permissions.BasePermission):
    """
    Base permission class for organization-scoped objects.

    Follows Template Method Pattern - provides common organization scoping logic.
    """

    def has_permission(self, request, view):
        """Check basic organization membership."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        return organization is not None

    def has_object_permission(self, request, view, obj):
        """Check if object belongs to user's organization."""
        if not request.user.is_authenticated:
            return False

        organization = getattr(request, 'organization', None)
        if not organization:
            return False

        # Check if object belongs to the same organization
        return getattr(obj, 'organization', None) == organization


class TimeEntryPermission(permissions.BasePermission):
    """
    Custom permission for time entries.

    Follows Single Responsibility Principle - only handles time entry access.
    """

    def has_object_permission(self, request, view, obj):
        """Check time entry permissions."""
        if not request.user.is_authenticated:
            return False

        # Owner can always access their time entries
        if obj.user == request.user:
            return True

        # Managers can access their team's time entries
        if hasattr(request.user, 'can_manage_user'):
            return request.user.can_manage_user(obj.user)

        # Project managers can access project time entries
        if obj.project and obj.project.project_manager == request.user:
            return True

        return False


class TaskPermission(permissions.BasePermission):
    """
    Custom permission for tasks.

    Follows Single Responsibility Principle - only handles task access.
    """

    def has_object_permission(self, request, view, obj):
        """Check task permissions."""
        if not request.user.is_authenticated:
            return False

        # Task assignee can access
        if obj.assigned_to == request.user:
            return True

        # Task creator can access
        if obj.created_by == request.user:
            return True

        # Project manager can access
        if obj.project.project_manager == request.user:
            return True

        # Team members can access project tasks
        if obj.project.can_user_log_time(request.user):
            return True

        return False