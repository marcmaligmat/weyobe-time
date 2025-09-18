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
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_active = serializers.ReadOnlyField()
    is_overtime = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()

    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_name', 'project', 'project_name',
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