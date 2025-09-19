from rest_framework import serializers
from .models import Project, Client, ProjectCategory, ProjectMembership, Team, TeamMember, Task


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


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer.
    """
    team_lead_name = serializers.CharField(source='team_lead.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'code', 'team_lead', 'team_lead_name',
            'department', 'department_name', 'member_count', 'max_members',
            'is_public', 'is_active', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class TeamMemberSerializer(serializers.ModelSerializer):
    """
    Team member serializer.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    is_current = serializers.ReadOnlyField()
    is_team_lead = serializers.ReadOnlyField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'team', 'team_name', 'user', 'user_name', 'user_email',
            'role', 'start_date', 'end_date', 'allocation_percentage',
            'is_active', 'is_current', 'is_team_lead', 'can_view_all_projects',
            'can_create_projects', 'can_manage_members', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """
    Task serializer.
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    parent_task_title = serializers.CharField(source='parent_task.title', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    hours_variance = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name',
            'parent_task', 'parent_task_title', 'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name', 'start_date', 'due_date',
            'completed_date', 'estimated_hours', 'actual_hours', 'status',
            'priority', 'progress_percentage', 'completion_percentage',
            'is_billable', 'requires_approval', 'is_milestone', 'is_active',
            'is_overdue', 'is_completed', 'hours_variance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'actual_hours', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create task with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        validated_data['organization'] = self.context['organization']
        return super().create(validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Task creation serializer with validation.
    """
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'parent_task', 'assigned_to',
            'start_date', 'due_date', 'estimated_hours', 'status', 'priority',
            'is_billable', 'requires_approval', 'is_milestone'
        ]

    def validate(self, attrs):
        """Validate task data."""
        # Validate project access
        project = attrs.get('project')
        user = self.context['request'].user

        if project and not project.can_user_log_time(user):
            raise serializers.ValidationError("You don't have access to this project")

        # Validate parent task
        parent_task = attrs.get('parent_task')
        if parent_task and parent_task.project != project:
            raise serializers.ValidationError("Parent task must belong to the same project")

        # Validate assigned user
        assigned_to = attrs.get('assigned_to')
        if assigned_to and project and not project.can_user_log_time(assigned_to):
            raise serializers.ValidationError("Assigned user doesn't have access to this project")

        return attrs

    def create(self, validated_data):
        """Create task with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        validated_data['organization'] = self.context['organization']
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Task update serializer.
    """
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'start_date', 'due_date',
            'estimated_hours', 'status', 'priority', 'progress_percentage',
            'is_billable', 'requires_approval', 'is_milestone', 'is_active'
        ]

    def validate(self, attrs):
        """Validate task updates."""
        # Check if user can edit this task
        user = self.context['request'].user
        if not self.instance.can_be_edited_by(user):
            raise serializers.ValidationError("You don't have permission to edit this task")

        return attrs


class ProjectDetailSerializer(ProjectSerializer):
    """
    Detailed project serializer with team and task counts.
    """
    team_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    team_members_count = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            'team_count', 'task_count', 'team_members_count'
        ]

    def get_team_count(self, obj):
        """Get number of teams assigned to project."""
        return obj.teams.filter(is_active=True).count()

    def get_task_count(self, obj):
        """Get number of tasks in project."""
        return obj.tasks.filter(is_active=True, is_deleted=False).count()

    def get_team_members_count(self, obj):
        """Get number of team members in project."""
        return obj.get_team_members().count()


class ProjectAssignTeamSerializer(serializers.Serializer):
    """
    Project team assignment serializer.
    """
    team_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    def validate_team_ids(self, value):
        """Validate team IDs."""
        organization = self.context['organization']
        valid_teams = Team.objects.filter(
            id__in=value,
            organization=organization,
            is_active=True,
            is_deleted=False
        )

        if len(valid_teams) != len(value):
            raise serializers.ValidationError("Some teams are not valid or don't exist")

        return value

    def save(self):
        """Assign teams to project."""
        project = self.context['project']
        team_ids = self.validated_data['team_ids']
        teams = Team.objects.filter(id__in=team_ids)
        project.teams.set(teams)
        return project