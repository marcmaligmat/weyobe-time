"""
User serializers following SOLID principles.

This module provides serializers that follow:
- Single Responsibility: Each serializer handles one specific data transformation
- Open/Closed: Extensible through inheritance
- Interface Segregation: Focused serializers for different use cases
- Dependency Inversion: Abstract serializer interfaces
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, ComplianceSettings, Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Role serializer.

    Follows Single Responsibility Principle - only handles role serialization.
    """

    class Meta:
        model = Role
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer.

    Follows Single Responsibility Principle - only handles profile data.
    """

    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'avatar', 'timezone', 'date_format', 'time_format', 'language',
            'email_notifications', 'sms_notifications', 'desktop_notifications'
        ]


class ComplianceSettingsSerializer(serializers.ModelSerializer):
    """
    Compliance settings serializer.

    Follows Single Responsibility Principle - only handles compliance settings.
    """

    class Meta:
        model = ComplianceSettings
        fields = [
            'max_hours_per_day', 'max_hours_per_week', 'max_consecutive_days',
            'require_breaks', 'break_after_hours', 'break_duration_minutes',
            'require_lunch', 'lunch_after_hours', 'lunch_duration_minutes',
            'overtime_rate_multiplier', 'night_shift_differential',
            'weekend_rate_multiplier', 'require_approval_for_overtime',
            'require_approval_for_time_edits', 'auto_approve_regular_hours'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for general use.

    Follows Single Responsibility Principle - only handles basic user data.
    """
    role_name = serializers.CharField(source='role_name', read_only=True)
    department_name = serializers.CharField(source='department_name', read_only=True)
    organization_name = serializers.CharField(source='organization_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'role_name',
            'organization', 'organization_name', 'department', 'department_name',
            'employee_id', 'hire_date', 'hourly_rate', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with nested relationships.

    Follows Open/Closed Principle - extends basic user serializer.
    """
    profile = UserProfileSerializer(read_only=True)
    compliance_settings = ComplianceSettingsSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    role_name = serializers.CharField(source='role_name', read_only=True)
    department_name = serializers.CharField(source='department_name', read_only=True)
    organization_name = serializers.CharField(source='organization_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'role_name',
            'organization', 'organization_name', 'department', 'department_name',
            'employee_id', 'hire_date', 'termination_date', 'hourly_rate',
            'salary', 'currency', 'manager', 'profile', 'compliance_settings',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User creation serializer with password handling.

    Follows Single Responsibility Principle - only handles user creation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'role', 'organization', 'department', 'employee_id', 'hire_date',
            'hourly_rate', 'manager'
        ]

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User update serializer without sensitive fields.

    Follows Interface Segregation Principle - focused on safe updates.
    """

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'department', 'employee_id',
            'hourly_rate', 'manager'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer.

    Follows Single Responsibility Principle - only handles password changes.
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        """Validate password change."""
        user = self.context['request'].user

        # Verify current password
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError("Current password is incorrect")

        # Confirm new password
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")

        return attrs

    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer for custom authentication.

    Follows Single Responsibility Principle - only handles login validation.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError('Invalid email or password')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')

            attrs['user'] = user
            return attrs

        raise serializers.ValidationError('Must include email and password')