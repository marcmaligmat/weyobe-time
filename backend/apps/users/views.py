"""
User views following SOLID principles.

This module provides user API views that follow:
- Single Responsibility: Each view handles one specific operation
- Open/Closed: Extensible through inheritance
- Interface Segregation: Focused permissions and filters
- Dependency Inversion: Abstract view interfaces
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import User, UserProfile, ComplianceSettings
from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserProfileSerializer,
    ComplianceSettingsSerializer
)


class UserListCreateView(generics.ListCreateAPIView):
    """
    List users or create new user.

    Follows Single Responsibility Principle - only handles user listing/creation.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['first_name', 'last_name', 'hire_date', 'created_at']
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        """Filter users by organization."""
        user = self.request.user
        if not user.organization:
            return User.objects.none()

        # Global admin can see all users
        if user.role and user.role.name == 'global_admin':
            return User.objects.filter(is_deleted=False)

        # Organization admin can see all users in organization
        if user.role and user.role.name == 'admin':
            return User.objects.filter(
                organization=user.organization,
                is_deleted=False
            )

        # Managers can see their direct reports and same department
        if user.role and user.role.name in ['manager', 'team_lead']:
            return User.objects.filter(
                organization=user.organization,
                department=user.department,
                is_deleted=False
            )

        # Regular users can only see themselves
        return User.objects.filter(id=user.id, is_deleted=False)

    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete user.

    Follows Single Responsibility Principle - only handles single user operations.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter users by organization and permissions."""
        user = self.request.user
        if not user.organization:
            return User.objects.none()

        # Global admin can access all users
        if user.role and user.role.name == 'global_admin':
            return User.objects.filter(is_deleted=False)

        # Organization admin can access all users in organization
        if user.role and user.role.name == 'admin':
            return User.objects.filter(
                organization=user.organization,
                is_deleted=False
            )

        # Managers can access their direct reports
        if user.role and user.role.name in ['manager', 'team_lead']:
            manageable_users = [user.id] + [
                report.id for report in user.get_all_reports()
            ]
            return User.objects.filter(
                id__in=manageable_users,
                organization=user.organization,
                is_deleted=False
            )

        # Regular users can only access themselves
        return User.objects.filter(id=user.id, is_deleted=False)

    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def perform_destroy(self, instance):
        """Soft delete user."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Get current user details.

    Follows Single Responsibility Principle - only handles current user data.
    """
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """
    Update user profile.

    Follows Single Responsibility Principle - only handles profile updates.
    """
    user = request.user
    if not user.profile:
        # Create profile if it doesn't exist
        from .models import UserProfile
        user.profile = UserProfile.objects.create()
        user.save()

    serializer = UserProfileSerializer(
        user.profile,
        data=request.data,
        partial=request.method == 'PATCH'
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_compliance_settings(request):
    """
    Update user compliance settings.

    Follows Single Responsibility Principle - only handles compliance settings.
    """
    user = request.user
    if not user.compliance_settings:
        # Create compliance settings if they don't exist
        from .models import ComplianceSettings
        user.compliance_settings = ComplianceSettings.objects.create()
        user.save()

    serializer = ComplianceSettingsSerializer(
        user.compliance_settings,
        data=request.data,
        partial=request.method == 'PATCH'
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password.

    Follows Single Responsibility Principle - only handles password changes.
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password changed successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request, user_id=None):
    """
    Get user statistics.

    Follows Single Responsibility Principle - only handles user statistics.
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
        # Check permissions
        if not request.user.can_manage_user(user) and request.user != user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        user = request.user

    # Calculate statistics (placeholder)
    stats = {
        'total_hours_this_month': 160.5,
        'overtime_hours_this_month': 8.5,
        'projects_count': 3,
        'approval_rate': 95.0,
        'attendance_rate': 98.0,
    }

    return Response(stats)