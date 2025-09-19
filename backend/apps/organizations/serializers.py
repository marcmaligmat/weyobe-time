from rest_framework import serializers
from .models import Organization, OrganizationSettings, Department, OrganizationMember, Invitation


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    settings = OrganizationSettingsSerializer(read_only=True)
    user_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'email', 'phone', 'website',
            'timezone', 'currency', 'is_active', 'subscription_plan',
            'max_users', 'user_count', 'settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'code', 'parent', 'manager',
            'manager_name', 'full_name', 'is_active', 'budget',
            'cost_center', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """
    Organization member serializer.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user', 'user_name', 'user_email', 'role', 'joined_at', 'left_at',
            'is_active', 'can_invite_users', 'can_manage_projects', 'can_manage_teams',
            'can_view_reports', 'can_manage_settings', 'can_manage_billing',
            'invited_by', 'invited_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'joined_at', 'invited_by', 'created_at', 'updated_at']


class InvitationSerializer(serializers.ModelSerializer):
    """
    Invitation serializer.
    """
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()

    class Meta:
        model = Invitation
        fields = [
            'id', 'organization', 'email', 'invited_by', 'invited_by_name',
            'role', 'department', 'department_name', 'message', 'status',
            'expires_at', 'accepted_at', 'accepted_by', 'is_expired',
            'is_pending', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'token', 'invited_by', 'status', 'expires_at', 'accepted_at',
            'accepted_by', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """Create invitation with current user as inviter."""
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)


class InvitationCreateSerializer(serializers.ModelSerializer):
    """
    Invitation creation serializer with validation.
    """
    emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        min_length=1
    )

    class Meta:
        model = Invitation
        fields = ['emails', 'role', 'department', 'message']

    def validate_emails(self, value):
        """Validate email list."""
        if len(value) > 50:  # Limit bulk invitations
            raise serializers.ValidationError("Cannot invite more than 50 users at once")
        return value

    def create(self, validated_data):
        """Create multiple invitations."""
        emails = validated_data.pop('emails')
        invitations = []

        for email in emails:
            invitation_data = validated_data.copy()
            invitation_data['email'] = email
            invitation_data['invited_by'] = self.context['request'].user
            invitation_data['organization'] = self.context['organization']

            # Check if invitation already exists
            existing = Invitation.objects.filter(
                organization=invitation_data['organization'],
                email=email,
                status='pending'
            ).first()

            if not existing:
                invitation = Invitation.objects.create(**invitation_data)
                invitations.append(invitation)

        return invitations


class InvitationAcceptSerializer(serializers.Serializer):
    """
    Invitation acceptance serializer.
    """
    token = serializers.CharField()

    def validate_token(self, value):
        """Validate invitation token."""
        try:
            invitation = Invitation.objects.get(token=value)
            if not invitation.is_pending:
                raise serializers.ValidationError("Invitation is not valid or has expired")
            self.invitation = invitation
            return value
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")

    def save(self):
        """Accept the invitation."""
        user = self.context['request'].user
        return self.invitation.accept(user)