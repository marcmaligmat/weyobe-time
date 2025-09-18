from rest_framework import serializers
from .models import Project, Client, ProjectCategory, ProjectMembership


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = '__all__'
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    total_hours_logged = serializers.ReadOnlyField()
    budget_utilization = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'code', 'client', 'client_name',
            'department', 'department_name', 'category', 'project_manager',
            'project_manager_name', 'start_date', 'end_date', 'deadline',
            'budget_hours', 'budget_amount', 'hourly_rate', 'is_billable',
            'billing_type', 'status', 'priority', 'progress_percentage',
            'total_hours_logged', 'budget_utilization', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ProjectMembership
        fields = [
            'id', 'project', 'project_name', 'user', 'user_name', 'role',
            'start_date', 'end_date', 'allocation_percentage', 'hourly_rate',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']