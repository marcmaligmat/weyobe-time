from rest_framework import serializers
from .models import Organization, OrganizationSettings, Department


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