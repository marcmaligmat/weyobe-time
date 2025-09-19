from rest_framework import serializers
from .models import TimeEntry, BreakEntry, TimeModificationRequest, TimesheetPeriod


class BreakEntrySerializer(serializers.ModelSerializer):
    duration_hours = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = BreakEntry
        fields = [
            'id', 'break_type', 'start_time', 'end_time', 'duration_minutes',
            'duration_hours', 'is_paid', 'notes', 'is_active'
        ]
        read_only_fields = ['id']


class TimeEntrySerializer(serializers.ModelSerializer):
    break_entries = BreakEntrySerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_active = serializers.ReadOnlyField()
    is_overtime = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()

    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_name', 'project', 'project_name', 'task', 'task_title',
            'department', 'department_name', 'date', 'clock_in', 'clock_out',
            'is_manual_entry', 'manual_start_time', 'manual_end_time',
            'regular_hours', 'overtime_hours', 'total_hours', 'break_hours',
            'is_billable', 'hourly_rate', 'billable_amount', 'description',
            'internal_notes', 'status', 'submitted_at', 'approved_by',
            'approved_at', 'approval_notes', 'is_active', 'is_overtime',
            'duration', 'break_entries', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'regular_hours', 'overtime_hours', 'total_hours',
            'break_hours', 'billable_amount', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        return super().create(validated_data)


class TimeModificationRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = TimeModificationRequest
        fields = [
            'id', 'time_entry', 'requested_by', 'requested_by_name',
            'requested_changes', 'reason', 'status', 'reviewed_by',
            'reviewed_by_name', 'reviewed_at', 'review_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimesheetPeriodSerializer(serializers.ModelSerializer):
    total_hours = serializers.ReadOnlyField(source='get_total_hours')
    total_billable_amount = serializers.ReadOnlyField(source='get_total_billable_amount')

    class Meta:
        model = TimesheetPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'is_open', 'is_locked',
            'submission_deadline', 'approval_deadline', 'payroll_processed',
            'total_hours', 'total_billable_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """
    Time entry creation serializer with validation.
    """
    class Meta:
        model = TimeEntry
        fields = [
            'project', 'task', 'department', 'date', 'clock_in', 'clock_out',
            'is_manual_entry', 'manual_start_time', 'manual_end_time',
            'is_billable', 'hourly_rate', 'description', 'internal_notes'
        ]

    def validate(self, attrs):
        """Validate time entry data."""
        user = self.context['request'].user
        project = attrs.get('project')
        task = attrs.get('task')

        # Validate project access
        if project and not project.can_user_log_time(user):
            raise serializers.ValidationError("You don't have access to this project")

        # Validate task belongs to project
        if task and project and task.project != project:
            raise serializers.ValidationError("Task must belong to the selected project")

        # Validate task access
        if task and not task.project.can_user_log_time(user):
            raise serializers.ValidationError("You don't have access to this task")

        # Check for overlapping time entries
        date = attrs.get('date')
        clock_in = attrs.get('clock_in')
        clock_out = attrs.get('clock_out')

        if clock_in and date:
            overlapping_entries = TimeEntry.objects.filter(
                user=user,
                date=date,
                clock_out__isnull=True,  # Active entries
                is_deleted=False
            )
            if overlapping_entries.exists():
                raise serializers.ValidationError("You already have an active time entry")

        return attrs

    def create(self, validated_data):
        """Create time entry with current user."""
        validated_data['user'] = self.context['request'].user
        validated_data['organization'] = self.context['organization']
        return super().create(validated_data)


class TimeEntryClockInSerializer(serializers.Serializer):
    """
    Time entry clock-in serializer.
    """
    project = serializers.UUIDField()
    task = serializers.UUIDField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_project(self, value):
        """Validate project exists and user has access."""
        from apps.projects.models import Project
        try:
            project = Project.objects.get(
                id=value,
                organization=self.context['organization'],
                is_active=True,
                is_deleted=False
            )
            if not project.can_user_log_time(self.context['request'].user):
                raise serializers.ValidationError("You don't have access to this project")
            return project
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")

    def validate_task(self, value):
        """Validate task exists and belongs to project."""
        if not value:
            return None

        from apps.projects.models import Task
        try:
            task = Task.objects.get(
                id=value,
                organization=self.context['organization'],
                is_active=True,
                is_deleted=False
            )
            return task
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task not found")

    def validate(self, attrs):
        """Validate clock-in data."""
        user = self.context['request'].user
        project = attrs.get('project')
        task = attrs.get('task')

        # Check for active time entries
        active_entries = TimeEntry.objects.filter(
            user=user,
            clock_out__isnull=True,
            is_deleted=False
        )
        if active_entries.exists():
            raise serializers.ValidationError("You already have an active time entry")

        # Validate task belongs to project
        if task and task.project != project:
            raise serializers.ValidationError("Task must belong to the selected project")

        return attrs

    def save(self):
        """Create new time entry."""
        from django.utils import timezone

        user = self.context['request'].user
        organization = self.context['organization']

        time_entry = TimeEntry.objects.create(
            user=user,
            organization=organization,
            project=self.validated_data['project'],
            task=self.validated_data.get('task'),
            date=timezone.now().date(),
            clock_in=timezone.now(),
            description=self.validated_data.get('description', ''),
            hourly_rate=user.hourly_rate
        )
        return time_entry


class TimeEntryClockOutSerializer(serializers.Serializer):
    """
    Time entry clock-out serializer.
    """
    description = serializers.CharField(required=False, allow_blank=True)

    def save(self):
        """Clock out active time entry."""
        from django.utils import timezone

        user = self.context['request'].user

        try:
            time_entry = TimeEntry.objects.get(
                user=user,
                clock_out__isnull=True,
                is_deleted=False
            )
            time_entry.clock_out = timezone.now()
            if self.validated_data.get('description'):
                time_entry.description = self.validated_data['description']
            time_entry.save()
            return time_entry
        except TimeEntry.DoesNotExist:
            raise serializers.ValidationError("No active time entry found")


class TimeEntryUpdateSerializer(serializers.ModelSerializer):
    """
    Time entry update serializer.
    """
    class Meta:
        model = TimeEntry
        fields = [
            'project', 'task', 'clock_in', 'clock_out', 'description',
            'internal_notes', 'is_billable'
        ]

    def validate(self, attrs):
        """Validate time entry updates."""
        user = self.context['request'].user

        # Check if user can edit this time entry
        if not self.instance.can_be_edited_by(user):
            raise serializers.ValidationError("You don't have permission to edit this time entry")

        # Validate project access if changing project
        project = attrs.get('project')
        if project and project != self.instance.project:
            if not project.can_user_log_time(user):
                raise serializers.ValidationError("You don't have access to the new project")

        # Validate task belongs to project
        task = attrs.get('task')
        if task and project and task.project != project:
            raise serializers.ValidationError("Task must belong to the selected project")

        return attrs


class BreakEntryCreateSerializer(serializers.ModelSerializer):
    """
    Break entry creation serializer.
    """
    class Meta:
        model = BreakEntry
        fields = ['time_entry', 'break_type', 'start_time', 'end_time', 'is_paid', 'notes']

    def validate_time_entry(self, value):
        """Validate time entry access."""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You can only add breaks to your own time entries")
        return value

    def create(self, validated_data):
        """Create break entry with organization."""
        validated_data['organization'] = self.context['organization']
        return super().create(validated_data)


class TimeEntryStartBreakSerializer(serializers.Serializer):
    """
    Start break serializer.
    """
    break_type = serializers.ChoiceField(choices=BreakEntry.BREAK_TYPE_CHOICES)
    is_paid = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def save(self):
        """Start a break for the active time entry."""
        from django.utils import timezone

        user = self.context['request'].user
        organization = self.context['organization']

        # Find active time entry
        try:
            time_entry = TimeEntry.objects.get(
                user=user,
                clock_out__isnull=True,
                is_deleted=False
            )
        except TimeEntry.DoesNotExist:
            raise serializers.ValidationError("No active time entry found")

        # Check if already on break
        active_break = BreakEntry.objects.filter(
            time_entry=time_entry,
            end_time__isnull=True
        ).first()

        if active_break:
            raise serializers.ValidationError("You are already on a break")

        # Create break entry
        break_entry = BreakEntry.objects.create(
            organization=organization,
            time_entry=time_entry,
            break_type=self.validated_data['break_type'],
            start_time=timezone.now(),
            is_paid=self.validated_data.get('is_paid', False),
            notes=self.validated_data.get('notes', '')
        )
        return break_entry


class TimeEntryEndBreakSerializer(serializers.Serializer):
    """
    End break serializer.
    """
    def save(self):
        """End the active break."""
        from django.utils import timezone

        user = self.context['request'].user

        # Find active break
        try:
            time_entry = TimeEntry.objects.get(
                user=user,
                clock_out__isnull=True,
                is_deleted=False
            )
            break_entry = BreakEntry.objects.get(
                time_entry=time_entry,
                end_time__isnull=True
            )
            break_entry.end_time = timezone.now()
            break_entry.save()
            return break_entry
        except (TimeEntry.DoesNotExist, BreakEntry.DoesNotExist):
            raise serializers.ValidationError("No active break found")