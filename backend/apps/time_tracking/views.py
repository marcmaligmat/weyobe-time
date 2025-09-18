from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import TimeEntry, BreakEntry, TimeModificationRequest
from .serializers import (
    TimeEntrySerializer, BreakEntrySerializer,
    TimeModificationRequestSerializer
)


class TimeEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TimeEntry.objects.filter(
            organization=user.organization,
            is_deleted=False
        )

        # Filter by user if not manager/admin
        if not user.has_any_role(['manager', 'admin', 'global_admin']):
            queryset = queryset.filter(user=user)

        # Apply filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date', '-clock_in')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            organization=self.request.user.organization
        )


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TimeEntry.objects.filter(
            organization=user.organization,
            is_deleted=False
        )

        # Filter by user if not manager/admin
        if not user.has_any_role(['manager', 'admin', 'global_admin']):
            queryset = queryset.filter(user=user)

        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clock_in(request):
    """Start a new time entry (clock in)."""
    user = request.user
    now = timezone.now()

    # Check if user already has an active time entry
    active_entry = TimeEntry.objects.filter(
        user=user,
        clock_out__isnull=True,
        is_deleted=False
    ).first()

    if active_entry:
        return Response(
            {'error': 'You are already clocked in'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create new time entry
    project_id = request.data.get('project_id')
    description = request.data.get('description', '')

    time_entry = TimeEntry.objects.create(
        user=user,
        organization=user.organization,
        project_id=project_id if project_id else None,
        department=user.department,
        date=now.date(),
        clock_in=now,
        description=description,
        status='draft'
    )

    serializer = TimeEntrySerializer(time_entry)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clock_out(request):
    """End the current time entry (clock out)."""
    user = request.user
    now = timezone.now()

    # Find active time entry
    active_entry = TimeEntry.objects.filter(
        user=user,
        clock_out__isnull=True,
        is_deleted=False
    ).first()

    if not active_entry:
        return Response(
            {'error': 'No active time entry found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # End the time entry
    active_entry.clock_out = now
    active_entry.status = 'submitted'
    active_entry.save()

    serializer = TimeEntrySerializer(active_entry)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_break(request, time_entry_id):
    """Start a break for a time entry."""
    user = request.user
    time_entry = get_object_or_404(
        TimeEntry,
        id=time_entry_id,
        user=user,
        is_deleted=False
    )

    if not time_entry.is_active:
        return Response(
            {'error': 'Time entry is not active'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if there's already an active break
    active_break = time_entry.break_entries.filter(end_time__isnull=True).first()
    if active_break:
        return Response(
            {'error': 'Break is already active'},
            status=status.HTTP_400_BAD_REQUEST
        )

    break_type = request.data.get('break_type', 'short_break')
    notes = request.data.get('notes', '')

    break_entry = BreakEntry.objects.create(
        time_entry=time_entry,
        organization=user.organization,
        break_type=break_type,
        start_time=timezone.now(),
        notes=notes
    )

    serializer = BreakEntrySerializer(break_entry)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def end_break(request, time_entry_id):
    """End the current break for a time entry."""
    user = request.user
    time_entry = get_object_or_404(
        TimeEntry,
        id=time_entry_id,
        user=user,
        is_deleted=False
    )

    # Find active break
    active_break = time_entry.break_entries.filter(end_time__isnull=True).first()
    if not active_break:
        return Response(
            {'error': 'No active break found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    active_break.end_time = timezone.now()
    active_break.save()

    serializer = BreakEntrySerializer(active_break)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_time_entry(request):
    """Get the current active time entry for the user."""
    user = request.user
    active_entry = TimeEntry.objects.filter(
        user=user,
        clock_out__isnull=True,
        is_deleted=False
    ).first()

    if not active_entry:
        return Response({'active_entry': None})

    serializer = TimeEntrySerializer(active_entry)
    return Response({'active_entry': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def time_summary(request):
    """Get time summary for the user."""
    user = request.user
    today = timezone.now().date()

    # Today's summary
    today_entries = TimeEntry.objects.filter(
        user=user,
        date=today,
        is_deleted=False
    )

    today_total = sum(entry.total_hours for entry in today_entries)
    today_overtime = sum(entry.overtime_hours for entry in today_entries)

    # Week summary (simplified)
    week_total = today_total * 5  # Placeholder
    week_overtime = today_overtime * 5  # Placeholder

    return Response({
        'today': {
            'total_hours': today_total,
            'overtime_hours': today_overtime,
            'status': 'active' if today_entries.filter(clock_out__isnull=True).exists() else 'inactive'
        },
        'week': {
            'total_hours': week_total,
            'overtime_hours': week_overtime
        }
    })